"""Modular, explainable journal recommender.

The public ``recommend(...)`` signature is unchanged. Eligibility filters are
applied before retrieval and never influence the thematic score. The ranking
uses a reusable BM25F index, an optional local co-occurrence model and a
structured reranker; every additional module can be disabled for ablation.
"""
from collections import Counter
import re

import pandas as pd

from bm25f import BM25FIndex
from catalog_rules import integral_candidate
from manuscript_analysis import ManuscriptProfile, analyze_manuscript
from reranking import RerankedHit, rerank
from semantic import TopicCooccurrenceModel
from text_normalization import (
    CONTEXTUAL_TERMS,
    PHRASE_CONCEPTS,
    QUERY_EXPANSIONS,
    clean,
    contextual_expansions,
    find_phrase_concepts,
    phrase_terms,
    token_pairs,
    tokens,
)


class ModularJournalRecommender:
    """Local thematic ranker with explicit, switchable modules."""

    def __init__(self, catalog, *, use_analysis=True, use_semantic=False,
                 use_rerank=True, use_expansions=True,
                 use_contextual_expansions=True, semantic_weight=0.25):
        self.use_analysis = bool(use_analysis)
        self.use_semantic = bool(use_semantic)
        self.use_rerank = bool(use_rerank)
        self.use_expansions = bool(use_expansions)
        self.use_contextual_expansions = bool(use_contextual_expansions)
        self.semantic_weight = float(semantic_weight)
        self.frame = self._as_frame(catalog)
        self.index = BM25FIndex(self.frame)
        self.semantic = TopicCooccurrenceModel(self.index) if self.use_semantic else None
        self.topics = self._collect_topics()
        self.area_values = self._collect_area_values()

    @staticmethod
    def _as_frame(catalog):
        if isinstance(catalog, pd.DataFrame):
            frame = catalog.copy()
        else:
            frames = []
            for publisher, group in (catalog or {}).items():
                if publisher in {'INDICE', 'REQUISITOS', 'AVISOS'}:
                    continue
                current = group.copy()
                current['Editora'] = publisher
                frames.append(current)
            frame = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
        if frame.empty:
            frame = pd.DataFrame(columns=['Título da Revista', 'Editora', 'Cobertura APC', 'Modelo'])
        frame = frame.fillna('').reset_index(drop=True)
        if 'Editora' not in frame:
            frame['Editora'] = ''
        return frame

    def _collect_topics(self):
        column = self.index.topic_column
        if column is None:
            return [[] for _ in range(len(self.frame))]
        result = []
        for value in self.frame[column]:
            parts = [part.strip() for part in re.split(r'[;|\n]+', str(value)) if part.strip()]
            result.append(list(dict.fromkeys(parts)))
        return result

    def _collect_area_values(self):
        column = self.index.area_column
        if column is None:
            return [set() for _ in range(len(self.frame))]
        result = []
        for value in self.frame[column]:
            text = str(value).strip()
            if text and clean(text) != 'sem area identificada':
                result.append({text})
            else:
                result.append(set())
        return result

    def _flat_profile(self, profile):
        """Ablation profile: no role separation, no method penalty."""
        return ManuscriptProfile(
            title_terms=profile.title_terms,
            keyword_terms=profile.keyword_terms,
            abstract_terms=profile.abstract_terms,
            terms=profile.terms,
            focus_terms=profile.terms,
            phrase_concepts=profile.phrase_concepts,
            language=profile.language,
        )

    def _display_map(self, title='', abstract='', keywords=''):
        display = {}
        for text in (title, keywords, abstract):
            for term, raw in token_pairs(text):
                values = display.setdefault(term, [])
                if raw not in values:
                    values.append(raw)
        return display

    def _expanded_weights(self, profile):
        weights = Counter(profile.query_weights())
        if not self.use_expansions:
            return weights
        context = set(profile.terms)
        for term, weight in list(weights.items()):
            if self.use_contextual_expansions:
                alternatives = contextual_expansions(term, context)
            else:
                alternatives = QUERY_EXPANSIONS.get(term, (term,))
            if (self.use_contextual_expansions and term in CONTEXTUAL_TERMS
                    and len(alternatives) > 1):
                # In a network context, "segurança" means security more than
                # safety. Keep the original as a weaker alternative instead of
                # letting a safety journal lead the list.
                weights[term] *= 0.35
            for alternative in alternatives:
                if alternative == term:
                    continue
                # Expansion is a bounded alternative, never a second full vote.
                weights[alternative] = max(weights.get(alternative, 0.0), weight * 0.45)
        self._apply_phrase_concepts(weights, profile, context)
        return weights

    @staticmethod
    def _apply_phrase_concepts(weights, profile, context):
        """Keep a multiword concept from becoming its generic constituent word.

        "Deep learning" must not retrieve every education journal merely because
        it contains "learning". The phrase remains in the phrase index; here we
        only suppress the generic constituent and add bounded related terms when
        the surrounding text supplies a computing/imaging context.
        """
        for concept in profile.phrase_concepts:
            specification = PHRASE_CONCEPTS.get(concept)
            if not specification:
                continue
            concept_weight = max((weights.get(term, 0.0) for term in concept), default=0.0)
            for term in specification.get('suppress', ()):
                if term in weights:
                    weights[term] *= 0.18
            if concept_weight and context & set(specification.get('context', ())):
                # Related individual words are useful for \"neural\" and
                # \"network\", but do not re-inflate a generic constituent such
                # as \"learning\" after the phrase concept suppressed it.
                generic_constituents = {
                    term for phrase in PHRASE_CONCEPTS for term in phrase
                }
                for related in specification.get('related', ()):
                    for term in related:
                        if term in generic_constituents:
                            continue
                        weights[term] = max(weights.get(term, 0.0), concept_weight * 0.30)

    def _phrase_weights(self, title='', abstract='', keywords=''):
        phrases = Counter()
        sequences = (tokens(title), tokens(keywords), tokens(abstract))
        for text, weight in ((title, 3), (keywords, 4), (abstract, 1)):
            for phrase in phrase_terms(tokens(text)):
                phrases[phrase] = max(phrases.get(phrase, 0), weight)
        context = {term for sequence in sequences for term in sequence}
        for concept in find_phrase_concepts(sequences):
            specification = PHRASE_CONCEPTS.get(concept)
            if not specification or not context & set(specification.get('context', ())):
                continue
            base = max(phrases.get(' '.join(concept), 0.0), 1.0)
            for related in specification.get('related', ()):
                phrase = ' '.join(related)
                phrases[phrase] = max(phrases.get(phrase, 0.0), base * 0.35)
        return phrases

    def _allowed_indices(self, publishers, integral_only, areas):
        publishers = {publishers} if isinstance(publishers, str) else publishers
        publishers = set(publishers) if publishers is not None else None
        if publishers == set():
            return set()
        area_filter = {areas} if isinstance(areas, str) else (set(areas) if areas else None)
        if publishers is None and not integral_only and area_filter is None:
            return None
        allowed = set()
        for index, row in self.frame.iterrows():
            if publishers is not None and str(row.get('Editora', '')) not in publishers:
                continue
            if area_filter is not None and not (self.area_values[index] & area_filter):
                continue
            if integral_only and not integral_candidate(row):
                continue
            allowed.add(index)
        return allowed

    def _lexical_only(self, hits):
        if not hits:
            return []
        maximum = max(hit.score for hit in hits) or 1.0
        results = []
        for hit in hits:
            coverage = hit.coverage
            if coverage >= 0.50:
                label = 'Forte'
            elif coverage >= 0.30:
                label = 'Boa'
            elif coverage >= 0.15:
                label = 'Exploratória'
            else:
                label = 'Fraca'
            results.append(RerankedHit(
                hit=hit,
                score=hit.score / maximum,
                evidence=coverage,
                label=label,
                focus_coverage=0.0,
                matched_focus=(),
                matched_methods=(),
                semantic_terms=(),
                title_focus_count=0,
                topic_focus_count=0,
                area_match=False,
                method_only_match=False,
            ))
        return results

    def _select(self, candidates, limit, profile=None):
        """Return the requested page, retaining meaningful partial matches.

        Evidence labels describe uncertainty; they do not impose a 1/3/5-item
        limit. Method-only hits and candidates with no subject evidence stay out.
        """
        limit = max(1, min(int(limit), 30))
        core = set()
        if profile is not None:
            core = (set(profile.disease_terms) | set(profile.intervention_terms)
                    | set(profile.outcome_terms))
        def pertinent(candidate):
            if candidate.method_only_match or not candidate.matched_focus:
                return False
            matched = set(candidate.matched_focus)
            return (candidate.label != 'Fraca'
                    or candidate.domain_match
                    or len(core & matched) >= 2
                    or (profile is not None and not profile.population_terms
                        and len(matched) >= 2))
        usable = [candidate for candidate in candidates if pertinent(candidate)]
        strong = [c for c in usable if c.label in {'Forte', 'Boa'}]
        exploratory = [c for c in usable if c.label not in {'Forte', 'Boa'}]
        return (strong + exploratory)[:limit]

    def _diversify(self, candidates, limit):
        selected = []
        publisher_counts = Counter()
        area_counts = Counter()
        remaining = list(candidates)
        target = max(1, min(int(limit), 30))
        while remaining and len(selected) < target:
            best_position = 0
            best_value = None
            for position, candidate in enumerate(remaining):
                index = candidate.hit.index
                publisher = str(self.frame.iloc[index].get('Editora', ''))
                area = next(iter(sorted(self.area_values[index])), '')
                penalty = 1 + 0.12 * publisher_counts[publisher] + 0.06 * area_counts[area]
                value = candidate.score / penalty
                if best_value is None or value > best_value:
                    best_value = value
                    best_position = position
            candidate = remaining.pop(best_position)
            selected.append(candidate)
            index = candidate.hit.index
            publisher = str(self.frame.iloc[index].get('Editora', ''))
            area = next(iter(sorted(self.area_values[index])), '')
            publisher_counts[publisher] += 1
            area_counts[area] += 1
        return selected

    def _matched_topics(self, index, query_terms):
        matches = []
        for topic in self.topics[index]:
            overlap = set(query_terms) & set(tokens(topic))
            if overlap:
                matches.append((len(overlap), topic))
        matches.sort(key=lambda item: (-item[0], item[1]))
        return [topic for _, topic in matches[:3]]

    def _empty_result(self):
        result = self.frame.iloc[:0].copy()
        for column in ('Pontuação temática', 'Aderência', 'Cobertura temática',
                       'Evidência', 'Termos relacionados', 'Termos do seu texto',
                       'Temas relacionados', 'Perfil detectado'):
            result[column] = pd.Series(dtype='object')
        return result

    def recommend(self, title='', abstract='', keywords='', publishers=None, integral_only=True,
                  limit=10, areas=None, diversify=False, *, _broadening=False):
        # Bound work for callers outside the Streamlit form too.
        title, abstract, keywords = str(title or '')[:500], str(abstract or '')[:12000], str(keywords or '')[:1000]
        limit = max(1, min(int(limit), 30))
        profile = analyze_manuscript(title, abstract, keywords)
        display = self._display_map(title, abstract, keywords)
        if not profile.terms:
            return self._empty_result()
        ranking_profile = profile if self.use_analysis else self._flat_profile(profile)
        weights = self._expanded_weights(ranking_profile)
        phrases = self._phrase_weights(title, abstract, keywords)
        semantic_weights = Counter()
        if self.semantic is not None and self.use_semantic:
            semantic_weights = self.semantic.expand(
                ranking_profile.focus_terms or ranking_profile.terms,
                weight=self.semantic_weight,
                max_per_term=2,
            )
            for term, weight in semantic_weights.items():
                if term not in weights:
                    weights[term] = max(weights.get(term, 0.0), weight * 0.60)
        if not weights:
            return self._empty_result()
        allowed = self._allowed_indices(publishers, integral_only, areas)
        if allowed == set():
            return self._empty_result()
        top_k = min(200, max(80, int(limit) * 10))
        hits = self.index.search(weights, phrases=phrases, allowed_indices=allowed, top_k=top_k)
        if not hits:
            return self._empty_result()
        candidates = (
            rerank(ranking_profile, hits, semantic_weights=semantic_weights, top_k=top_k)
            if self.use_rerank else self._lexical_only(hits)
        )
        if diversify:
            core = set()
            if profile is not None:
                core = (set(profile.disease_terms)
                        | set(profile.intervention_terms)
                        | set(profile.outcome_terms))
            usable = [
                candidate for candidate in candidates
                if candidate.label != 'Fraca'
                or len(core & set(candidate.matched_focus)) >= 2
            ]
            if not usable:
                usable = self._select(candidates, 3, profile)
            cap = self._selection_cap(usable, limit)
            # Diversify a wider pool than the requested page so a second
            # publisher can enter the first page, while preserving the short
            # list rule for exploratory/weak evidence.
            selected = self._diversify(usable[:max(cap * 4, cap)], cap)
        else:
            selected = self._select(candidates, limit, profile)
        if not selected:
            return self._empty_result()

        indices = [candidate.hit.index for candidate in selected]
        result = self.frame.iloc[indices].copy()
        result['Pontuação temática'] = [round(candidate.score, 2) for candidate in selected]
        result['Aderência'] = [candidate.label for candidate in selected]
        result['Grupo de sugestões'] = ['Mais relacionadas' if candidate.label in {'Forte', 'Boa'} else 'Outras revistas para explorar' for candidate in selected]
        # Textual coverage is the weighted fraction of query terms found in the
        # journal record. Evidence is the reranker's heuristic, which also
        # includes role, field and domain signals. They are deliberately not
        # the same number.
        result['Cobertura temática'] = [round(candidate.hit.coverage * 100, 1) for candidate in selected]
        result['Evidência'] = [round(candidate.evidence * 100, 1) for candidate in selected]
        result['Termos relacionados'] = [
            ', '.join(list(dict.fromkeys(
                candidate.matched_focus + candidate.matched_methods + candidate.semantic_terms
            ))[:10])
            for candidate in selected
        ]
        result['Termos do seu texto'] = [
            ', '.join(list(dict.fromkeys(
                raw for term in (candidate.matched_focus + candidate.matched_methods)
                if term in display
                for raw in display[term]
            ))[:10])
            for candidate in selected
        ]
        result['Temas relacionados'] = [
            '; '.join(self._matched_topics(candidate.hit.index, profile.terms))
            for candidate in selected
        ]
        result['Perfil detectado'] = profile.summary
        result['Origem da sugestão'] = 'Correspondência com o manuscrito'
        # A second, bounded retrieval widens the subject rather than filling
        # slots with weak accidental matches. Preserve every eligibility filter.
        if not _broadening and len(result) < limit:
            bridges = {
                'probiotic': ('gut', 'microbiome', 'nutrition', 'veterinary'),
                'swine': ('veterinary', 'livestock', 'nutrition'),
                'chicken': ('poultry', 'animal', 'nutrition', 'veterinary'),
                'leishmaniasis': ('parasite', 'parasitology', 'veterinary'),
                'cybersecurity': ('network', 'security', 'computer'),
            }
            related = list(dict.fromkeys(t for term in profile.terms for t in bridges.get(term, ())))
            if related:
                broader = self.recommend(
                    title=title, abstract=abstract, keywords=keywords + '; ' + '; '.join(related),
                    publishers=publishers, integral_only=integral_only, limit=limit,
                    areas=areas, diversify=diversify, _broadening=True)
                broader = broader.loc[~broader.index.isin(result.index)].copy()
                if not broader.empty:
                    broader['Aderência'] = 'Exploratória — busca ampliada'
                    broader['Grupo de sugestões'] = 'Outras revistas para explorar'
                    broader['Origem da sugestão'] = 'Busca ampliada por temas relacionados: ' + ', '.join(related)
                    broader['Cobertura temática'] = float('nan')
                    broader['Evidência'] = float('nan')
                    result = pd.concat([result, broader]).iloc[:limit].copy()
        return result

    def query_terms(self, title='', abstract='', keywords=''):
        profile = analyze_manuscript(title, abstract, keywords)
        ranking_profile = profile if self.use_analysis else self._flat_profile(profile)
        weights = self._expanded_weights(ranking_profile)
        return list(weights)

    def query_labels(self, title='', abstract='', keywords=''):
        profile = analyze_manuscript(title, abstract, keywords)
        display = self._display_map(title, abstract, keywords)
        labels = []
        ordered_terms = list(dict.fromkeys(
            profile.focus_terms + profile.method_terms + profile.terms
        ))
        for term in ordered_terms:
            for raw in display.get(term, [term]):
                if raw not in labels:
                    labels.append(raw)
        return labels
"""BM25F-style lexical retrieval with explicit field evidence.

The index is built once and reused for every query. It uses only the local
catalogue frame; no manuscript text is sent anywhere or written to disk.
"""
from collections import Counter, defaultdict
from dataclasses import dataclass
from math import log

from text_normalization import label_key, tokens


TITLE_ALIASES = {'titulo da revista', 'titulo', 'journal title', 'revista', 'periodico', 'title'}
TOPIC_ALIASES = {
    'temas openalex', 'topicos openalex', 'topics', 'topic', 'temas', 'topicos',
    'tema', 'topico', 'openalex topics', 'openalex topic',
}
AREA_ALIASES = {
    'area openalex', 'area', 'subject area', 'field', 'disciplina', 'grande area',
    'area do conhecimento', 'areas',
}
KEYWORD_ALIASES = {
    'palavras chave', 'palavra chave', 'keywords', 'keyword', 'assunto', 'assuntos',
    'descritores', 'termos',
}
SCOPE_ALIASES = {
    'escopo', 'escopo da revista', 'aims and scope', 'aims scope', 'objetivo',
    'objetivos', 'descricao', 'description', 'foco', 'linha editorial', 'about',
    'sobre', 'publico alvo', 'tipos de artigo', 'article types', 'scope',
    'journal scope', 'about the journal', 'sobre a revista', 'descricao da revista',
}


@dataclass(frozen=True)
class RetrievalHit:
    """One lexical candidate, with enough evidence for reranking and display."""

    index: int
    score: float
    matched_terms: tuple
    coverage: float
    field_matches: tuple
    phrase_matches: tuple
    terms: tuple
    title_terms: tuple
    topic_terms: tuple
    area_terms: tuple
    keyword_terms: tuple
    scope_terms: tuple

    def fields_for(self, term):
        for current, fields in self.field_matches:
            if current == term:
                return fields
        return ()


def _find_column(frame, aliases):
    for column in frame.columns:
        if label_key(column) in aliases:
            return column
    return None


def _as_text(value):
    if isinstance(value, (list, tuple, set)):
        return '; '.join(str(item) for item in value if item is not None)
    if value is None:
        return ''
    try:
        if value != value:  # NaN
            return ''
    except Exception:
        pass
    return str(value)


def _window_contains(sequence, phrase):
    size = len(phrase)
    if not size or size > len(sequence):
        return False
    return any(tuple(sequence[position:position + size]) == phrase
               for position in range(len(sequence) - size + 1))


class BM25FIndex:
    """Reusable weighted-field index.

    Field weights are the established title/topics/area/keywords/scope weights.
    The implementation is a BM25F-style weighted-term approximation: field
    frequencies are combined before saturation, while field presence is kept
    for explanations and reranking.
    """

    K1 = 1.5
    B = 0.75
    FIELD_WEIGHTS = {'title': 3.0, 'topics': 2.0, 'area': 1.5, 'keywords': 2.0, 'scope': 1.0}

    def __init__(self, frame):
        self.frame = frame
        self.title_column = _find_column(frame, TITLE_ALIASES)
        self.topic_column = _find_column(frame, TOPIC_ALIASES)
        self.area_column = _find_column(frame, AREA_ALIASES)
        self.keyword_column = _find_column(frame, KEYWORD_ALIASES)
        self.scope_column = _find_column(frame, SCOPE_ALIASES)
        self._build()

    def _value(self, index, field):
        column = {
            'title': self.title_column,
            'topics': self.topic_column,
            'area': self.area_column,
            'keywords': self.keyword_column,
            'scope': self.scope_column,
        }[field]
        if column is None:
            return ''
        # Publisher and OpenAlex fields can coexist; preserve both sources.
        aliases = {'title': TITLE_ALIASES, 'topics': TOPIC_ALIASES,
                   'area': AREA_ALIASES, 'keywords': KEYWORD_ALIASES,
                   'scope': SCOPE_ALIASES}[field]
        values = [_as_text(self.frame.iloc[index][name]) for name in self.frame.columns
                  if label_key(name) in aliases]
        return '; '.join(dict.fromkeys(value for value in values if value))

    def _build(self):
        self.field_tokens = {field: [] for field in self.FIELD_WEIGHTS}
        self.field_terms = {field: [] for field in self.FIELD_WEIGHTS}
        self.weighted_tf = []
        self.weighted_length = []
        self.postings = defaultdict(set)
        self.document_frequency = Counter()
        self.all_terms = []

        for index in range(len(self.frame)):
            combined = Counter()
            per_field_terms = {}
            for field, weight in self.FIELD_WEIGHTS.items():
                sequence = tuple(tokens(self._value(index, field)))
                term_set = tuple(dict.fromkeys(sequence))
                self.field_tokens[field].append(sequence)
                self.field_terms[field].append(term_set)
                per_field_terms[field] = term_set
                for term, count in Counter(sequence).items():
                    combined[term] += weight * count
            self.weighted_tf.append(combined)
            self.weighted_length.append(sum(combined.values()))
            terms = tuple(dict.fromkeys(term for field in self.FIELD_WEIGHTS for term in per_field_terms[field]))
            self.all_terms.append(terms)
            for term in combined:
                self.postings[term].add(index)
                self.document_frequency[term] += 1

        self.average_length = (sum(self.weighted_length) / len(self.weighted_length)) if self.weighted_length else 0.0

    def __len__(self):
        return len(self.frame)

    def idf(self, term):
        frequency = self.document_frequency.get(term, 0)
        if not frequency:
            return 0.0
        total = len(self.frame)
        return log(1 + (total - frequency + 0.5) / (frequency + 0.5))

    def search(self, query_weights, phrases=None, allowed_indices=None, top_k=100):
        """Return the best lexical candidates for a weighted query.

        ``query_weights`` is a mapping term -> weight. ``phrases`` is an optional
        mapping phrase -> weight. ``allowed_indices`` is the eligibility mask
        computed outside the ranker; it never changes thematic scores.
        """
        weights = {term: float(weight) for term, weight in (query_weights or {}).items()
                   if term and float(weight) > 0}
        if not weights:
            return []
        allowed = set(allowed_indices) if allowed_indices is not None else None
        candidates = set()
        for term in weights:
            if self.document_frequency.get(term):
                candidates.update(self.postings[term])
        if allowed is not None:
            candidates.intersection_update(allowed)
        if not candidates:
            return []

        phrase_weights = {phrase: float(weight) for phrase, weight in (phrases or {}).items()
                          if phrase and float(weight) > 0}
        total_query_weight = sum(weights.values())
        scored = []
        for index in candidates:
            combined = self.weighted_tf[index]
            length = self.weighted_length[index]
            norm = self.K1 * (1 - self.B + self.B * (length / self.average_length if self.average_length else 1))
            score = 0.0
            matched = []
            matched_weight = 0.0
            field_matches = []
            for term, weight in weights.items():
                frequency = combined.get(term, 0)
                if not frequency:
                    continue
                score += weight * self.idf(term) * (frequency * (self.K1 + 1)) / (frequency + norm)
                matched.append(term)
                matched_weight += weight
                fields = tuple(field for field in self.FIELD_WEIGHTS
                               if term in self.field_terms[field][index])
                field_matches.append((term, fields))

            phrase_matches = []
            for phrase, weight in phrase_weights.items():
                phrase_tokens = tuple(phrase.split())
                fields = []
                for field in self.FIELD_WEIGHTS:
                    if _window_contains(self.field_tokens[field][index], phrase_tokens):
                        fields.append(field)
                if fields:
                    # Phrase evidence is a bounded bonus, not a replacement for
                    # individual term evidence.
                    score += min(weight, 4.0) * 0.18 * len(fields)
                    phrase_matches.append((phrase, tuple(fields)))

            if not matched and not phrase_matches:
                continue
            coverage = matched_weight / total_query_weight if total_query_weight else 0.0
            scored.append(RetrievalHit(
                index=index,
                score=score,
                matched_terms=tuple(matched),
                coverage=coverage,
                field_matches=tuple(field_matches),
                phrase_matches=tuple(phrase_matches),
                terms=self.all_terms[index],
                title_terms=self.field_terms['title'][index],
                topic_terms=self.field_terms['topics'][index],
                area_terms=self.field_terms['area'][index],
                keyword_terms=self.field_terms['keywords'][index],
                scope_terms=self.field_terms['scope'][index],
            ))

        scored.sort(key=lambda hit: (-hit.score, hit.index))
        return scored[:max(1, int(top_k))]

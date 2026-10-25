"""Rule-based manuscript analysis for thematic journal retrieval.

This is deliberately a transparent rule system, not a trained model. It
separates the central subject (disease, population, intervention, outcome)
from auxiliary methods such as "molecular" or "diagnosis". The output is a
profile, not a CAPES eligibility decision and not a probability of acceptance.
"""
from collections import Counter
from dataclasses import dataclass

from text_normalization import (
    AREA_TERMS,
    DISEASE_TERMS,
    INTERVENTION_TERMS,
    METHOD_TERMS,
    OUTCOME_TERMS,
    POPULATION_TERMS,
    clean,
    find_phrase_concepts,
    tokens,
)


PT_HINTS = {
    'de', 'da', 'do', 'das', 'dos', 'em', 'para', 'com', 'uma', 'um', 'nao',
    'saude', 'doenca', 'estudo', 'pesquisa', 'avaliacao', 'producao', 'sistema',
    'bem', 'estar', 'entre', 'sobre', 'por', 'como', 'mais', 'menos',
}
EN_HINTS = {
    'the', 'and', 'of', 'in', 'for', 'with', 'health', 'disease', 'study',
    'research', 'evaluation', 'production', 'system', 'between', 'about',
    'from', 'using', 'analysis', 'effects', 'effect',
}
GENERIC_TERMS = {
    'science', 'scientific', 'research', 'study', 'article', 'journal',
    'review', 'data', 'result', 'method', 'analysis', 'approach', 'paper',
    'sistema', 'investiga', 'indicadore',
}


@dataclass(frozen=True)
class ManuscriptProfile:
    """Structured, explainable view of the visitor's text."""

    title_terms: tuple = ()
    keyword_terms: tuple = ()
    abstract_terms: tuple = ()
    terms: tuple = ()
    disease_terms: tuple = ()
    population_terms: tuple = ()
    intervention_terms: tuple = ()
    outcome_terms: tuple = ()
    method_terms: tuple = ()
    area_terms: tuple = ()
    focus_terms: tuple = ()
    secondary_terms: tuple = ()
    phrase_concepts: tuple = ()
    method_only: bool = False
    language: str = 'unknown'

    @property
    def central_terms(self):
        """The problem/population/intervention core, excluding auxiliary methods."""
        return self.focus_terms

    @property
    def has_focus(self):
        return bool(self.focus_terms)

    @property
    def summary(self):
        blocks = []
        for label, values in (
            ('doença', self.disease_terms),
            ('população', self.population_terms),
            ('intervenção', self.intervention_terms),
            ('desfecho', self.outcome_terms),
            ('método auxiliar', self.method_terms),
            ('área', self.area_terms),
        ):
            if values:
                blocks.append(f'{label}: ' + ', '.join(values[:6]))
        if not blocks:
            return 'Nenhum conceito temático reconhecido.'
        return '; '.join(blocks)

    def query_weights(self):
        """Field-aware term weights with focus/method separation.

        Title, keywords and abstract keep the established 3/4/1 field weights.
        Focus terms receive a boost; when a focus exists, auxiliary methods are
        down-weighted rather than allowed to dominate the query.
        """
        weights = Counter()
        for terms, base in (
            (self.title_terms, 3),
            (self.keyword_terms, 4),
            (self.abstract_terms, 1),
        ):
            for term in set(terms):
                weights[term] += base
        focus = set(self.focus_terms)
        methods = set(self.method_terms)
        areas = set(self.area_terms)
        for term in list(weights):
            if term in focus:
                weights[term] *= 1.8
            elif term in methods:
                weights[term] *= 0.45 if focus else 1.0
            elif term in areas:
                weights[term] *= 0.8
        return weights


def _unique(values):
    return tuple(dict.fromkeys(value for value in values if value))


def detect_language(title='', abstract='', keywords=''):
    words = {clean(word) for word in (str(title) + ' ' + str(abstract) + ' ' + str(keywords)).split()}
    pt = len(words & PT_HINTS)
    en = len(words & EN_HINTS)
    if pt and en:
        return 'mixed'
    if pt:
        return 'pt'
    if en:
        return 'en'
    return 'unknown'


def analyze_manuscript(title='', abstract='', keywords=''):
    """Extract central subject, population, disease, intervention, method and area.

    Rules are local and inspectable. A term is never treated as a journal
    title hint; the analyzer only assigns semantic roles to manuscript terms.
    """
    title_terms = _unique(tokens(title))
    keyword_terms = _unique(tokens(keywords))
    abstract_terms = _unique(tokens(abstract))
    all_terms = _unique(title_terms + keyword_terms + abstract_terms)

    disease = tuple(term for term in all_terms if term in DISEASE_TERMS)
    population = tuple(term for term in all_terms if term in POPULATION_TERMS)
    intervention = tuple(term for term in all_terms if term in INTERVENTION_TERMS)
    outcome = tuple(term for term in all_terms if term in OUTCOME_TERMS)
    method = tuple(term for term in all_terms if term in METHOD_TERMS)
    area = tuple(term for term in all_terms if term in AREA_TERMS)

    # Content terms are the non-method remainder. They keep the central
    # application domain alive when there is no explicit disease/population.
    content = tuple(
        term for term in all_terms
        if term not in METHOD_TERMS and term not in GENERIC_TERMS
    )
    focus = _unique(disease + population + intervention + outcome + content)
    secondary = tuple(term for term in method if term not in set(focus))
    method_only = bool(method) and not focus
    phrase_concepts = find_phrase_concepts((title_terms, keyword_terms, abstract_terms))

    return ManuscriptProfile(
        title_terms=title_terms,
        keyword_terms=keyword_terms,
        abstract_terms=abstract_terms,
        terms=all_terms,
        disease_terms=disease,
        population_terms=population,
        intervention_terms=intervention,
        outcome_terms=outcome,
        method_terms=method,
        area_terms=area,
        focus_terms=focus,
        secondary_terms=secondary,
        phrase_concepts=phrase_concepts,
        method_only=method_only,
        language=detect_language(title, abstract, keywords),
    )

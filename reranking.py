"""Pertinence reranking for lexical and semantic candidates.

The reranker combines three signals: normalized lexical evidence, bounded
topic co-occurrence evidence, and structured manuscript roles. It explicitly
penalizes candidates that match only an auxiliary method when the manuscript
has a disease, population, intervention or outcome.
"""
from dataclasses import dataclass


ANIMAL_POPULATIONS = {
    'animal', 'dog', 'cat', 'cattle', 'goat', 'sheep', 'horse', 'fish', 'bee',
    'bird', 'poultry', 'chicken', 'swine', 'livestock',
}
PRODUCTION_ANIMALS = {
    'cattle', 'goat', 'sheep', 'horse', 'fish', 'bee', 'poultry', 'chicken',
    'swine', 'livestock',
}
PLANT_POPULATIONS = {'plant', 'crop'}
HUMAN_POPULATIONS = {
    'human', 'patient', 'child', 'adolescent', 'elderly', 'woman', 'man',
    'worker', 'student', 'teacher', 'consumer', 'farmer', 'family', 'community',
}
ANIMAL_HINTS = {
    'animal', 'veterinary', 'livestock', 'poultry', 'agriculture', 'agronomy',
    'zoology', 'biology', 'food', 'fisheries', 'reproduction', 'nutrition',
    'parasitology', 'medicine', 'immunology', 'microbiology', 'epidemiology',
}
STRONG_PRODUCTION_HINTS = {
    'livestock', 'poultry', 'agriculture', 'agronomy', 'food', 'nutrition',
    'production', 'farm',
}
PRODUCTION_HINTS = STRONG_PRODUCTION_HINTS | {'veterinary'}
PLANT_HINTS = {
    'plant', 'agriculture', 'agronomy', 'botany', 'crop', 'soil', 'environment',
    'forest', 'seed', 'irrigation', 'food',
}
# Broad agricultural terms also occur in animal-science venues. These stricter
# hints identify a plant/crop context without excluding livestock nutrition.
STRICT_PLANT_HINTS = {'plant', 'botany', 'crop', 'soil', 'forest', 'seed', 'irrigation'}
HUMAN_HINTS = {
    'medicine', 'health', 'nursing', 'psychology', 'psychiatry', 'public',
    'epidemiology', 'dentistry', 'pharmacy', 'rehabilitation', 'education',
    'sociology', 'occupational',
}
HEALTH_HINTS = {
    'medicine', 'health', 'veterinary', 'immunology', 'microbiology',
    'parasitology', 'pharmacy', 'nursing', 'biology', 'biochemistry',
}
NON_PRODUCTION_HINTS = {
    'laboratory', 'lab', 'primatology', 'primate', 'primates', 'marine',
    'mammal', 'wildlife', 'zoo', 'exotic', 'pet',
}
ETHICS_HINTS = {'ethics', 'philosophy', 'philosophical', 'law', 'policy', 'political'}


@dataclass(frozen=True)
class RerankedHit:
    hit: object
    score: float
    evidence: float
    label: str
    focus_coverage: float
    matched_focus: tuple
    matched_methods: tuple
    semantic_terms: tuple
    title_focus_count: int
    topic_focus_count: int
    area_match: bool
    method_only_match: bool
    domain_match: bool = False


def _role_weights(profile):
    # The problem/intervention/outcome is the central subject. Population is
    # important but must not let a generic animal/health journal outrank a
    # journal that matches two central AMR concepts while omitting the host.
    weights = {}
    for term in profile.disease_terms:
        weights[term] = max(weights.get(term, 0.0), 1.8)
    for term in profile.population_terms:
        weights[term] = max(weights.get(term, 0.0), 1.0)
    for term in profile.intervention_terms:
        weights[term] = max(weights.get(term, 0.0), 1.3)
    for term in profile.outcome_terms:
        weights[term] = max(weights.get(term, 0.0), 1.6)
    for term in profile.focus_terms:
        weights.setdefault(term, 0.6)
    return weights


def _coverage(terms, target):
    if not target:
        return 0.0
    target = set(target)
    return sum(1 for term in terms if term in target) / len(target)


def _domain_match(profile, hit_terms):
    terms = set(hit_terms)
    populations = set(profile.population_terms)
    if populations & PRODUCTION_ANIMALS:
        if terms & NON_PRODUCTION_HINTS and not (terms & STRONG_PRODUCTION_HINTS):
            return False
        # "Plants and Animals" in a plant-breeding topic is not evidence of a
        # production-animal venue. Require a specific animal anchor when the
        # record has a strict plant/crop signal.
        if terms & STRICT_PLANT_HINTS and not (
                terms & {'veterinary', 'poultry', 'cattle', 'swine', 'goat',
                         'sheep', 'horse', 'fish', 'bee'}):
            return False
        anchor = terms & (PRODUCTION_ANIMALS | {'animal', 'veterinary'})
        topic = terms & {'behavior', 'welfare', 'nutrition', 'production', 'reproduction', 'health', 'science'}
        return bool(anchor and (topic or (terms & STRONG_PRODUCTION_HINTS)))
    if populations & ANIMAL_POPULATIONS:
        return bool(terms & ANIMAL_HINTS)
    if populations & PLANT_POPULATIONS:
        return bool(terms & PLANT_HINTS)
    if populations & HUMAN_POPULATIONS:
        return bool(terms & HUMAN_HINTS)
    if profile.disease_terms:
        return bool(terms & HEALTH_HINTS)
    return False


def _label(profile, evidence, focus_coverage, title_focus_count, topic_focus_count,
           matched_focus, method_only_match, coverage, domain_match, population_match,
           disease_match):
    if profile.focus_terms:
        disease_or_population = bool(profile.disease_terms or profile.population_terms)
        role_match = disease_match or population_match
        if profile.disease_terms and not disease_match:
            if profile.population_terms and population_match and matched_focus:
                return 'Exploratória'
            return 'Exploratória' if (domain_match and matched_focus) else 'Fraca'
        if profile.population_terms and not population_match and not disease_match:
            core_terms = (set(profile.disease_terms)
                          | set(profile.intervention_terms)
                          | set(profile.outcome_terms))
            core_matches = set(matched_focus) & core_terms
            # A journal can be pertinent to the problem (for example,
            # antimicrobial resistance) without naming the host population.
            # Keep it as exploratory instead of discarding it as Fraca.
            if matched_focus and (domain_match or len(core_matches) >= 2):
                return 'Exploratória'
            return 'Fraca'
        if profile.population_terms and not domain_match:
            # A matching generic word such as "animal" in a plant-breeding
            # topic is not enough to call a production-animal venue Boa.
            return 'Exploratória' if matched_focus else 'Fraca'
        if (evidence >= 0.55 and focus_coverage >= 0.55
                and (not disease_or_population or role_match)
                and (title_focus_count or topic_focus_count)):
            return 'Forte'
        if evidence >= 0.32 and focus_coverage >= 0.30 and (title_focus_count or topic_focus_count):
            return 'Boa'
        if matched_focus and not method_only_match:
            return 'Exploratória'
        return 'Fraca'
    if coverage >= 0.50 and (title_focus_count or topic_focus_count):
        return 'Forte'
    if coverage >= 0.30:
        return 'Boa'
    if coverage >= 0.15:
        return 'Exploratória'
    return 'Fraca'


def rerank(profile, hits, semantic_weights=None, top_k=100):
    """Rerank lexical hits using structured focus and bounded semantics."""
    if not hits:
        return []
    semantic_weights = dict(semantic_weights or {})
    semantic_total = sum(float(weight) for weight in semantic_weights.values())
    role_weights = _role_weights(profile)
    role_total = sum(role_weights.values())
    focus_terms = set(profile.focus_terms)
    method_terms = set(profile.method_terms)
    population_terms = set(profile.population_terms)
    disease_terms = set(profile.disease_terms)
    core_terms = (
        disease_terms
        | set(profile.intervention_terms)
        | set(profile.outcome_terms)
    )
    area_terms = set(profile.area_terms)
    maximum_lexical = max(hit.score for hit in hits) or 1.0
    reranked = []

    for hit in hits:
        # Explicit journal specialisms outweigh generic animal-welfare topics.
        # This is a domain rule, not a list of journal names.
        title_specialism = set(hit.title_terms)
        if population_terms & {'poultry', 'chicken', 'cattle', 'swine', 'goat', 'sheep'}:
            incompatible = title_specialism & {'primatology', 'primate', 'marine', 'laboratory', 'lab'}
            if incompatible and not (title_specialism & (population_terms - {'animal'})):
                continue
        computational_focus = set(profile.terms) & {'cybersecurity', 'intrusion', 'security'}
        if computational_focus and set(profile.terms) & {'network', 'computer'}:
            unrelated_domain = title_specialism & {'sea', 'ocean', 'oceanography', 'marine'}
            if unrelated_domain and not (title_specialism & {'network', 'computer', 'computing', 'security'}):
                continue
        hit_terms = set(hit.terms)
        matched_focus = tuple(term for term in profile.focus_terms if term in hit_terms)
        matched_methods = tuple(term for term in profile.method_terms if term in hit_terms)
        matched_semantic = tuple(term for term in semantic_weights if term in hit_terms)
        semantic_coverage = (
            sum(float(semantic_weights[term]) for term in matched_semantic) / semantic_total
            if semantic_total else 0.0
        )
        focus_weight = sum(role_weights.get(term, 0.0) for term in matched_focus)
        focus_coverage = focus_weight / role_total if role_total else 0.0
        title_terms = set(hit.title_terms)
        topic_terms = set(hit.topic_terms)
        title_focus_count = len(focus_terms & title_terms)
        topic_focus_count = len(focus_terms & topic_terms)
        title_coverage = _coverage(title_terms, focus_terms)
        topic_coverage = _coverage(topic_terms, focus_terms)
        area_match = bool(area_terms & (set(hit.area_terms) | title_terms | topic_terms))
        method_only_match = bool(profile.focus_terms and not matched_focus and matched_methods)
        disease_match = bool(disease_terms & hit_terms)
        population_match = bool(population_terms & hit_terms)
        core_matches = set(matched_focus) & core_terms
        context_terms = hit_terms | title_terms | topic_terms | set(hit.area_terms)
        domain_match = _domain_match(profile, context_terms)
        lexical_norm = hit.score / maximum_lexical if maximum_lexical else 0.0

        if profile.focus_terms:
            structured = (
                0.55 * focus_coverage
                + 0.20 * title_coverage
                + 0.15 * topic_coverage
                + 0.10 * (1.0 if area_match else 0.0)
            )
            score = 0.50 * lexical_norm + 0.15 * semantic_coverage + 0.35 * structured
            if not matched_focus:
                score *= 0.35
            elif method_only_match:
                score *= 0.55
            if disease_match or population_match:
                score += 0.06
            if len(core_matches) >= 2:
                # Matching two central concepts (e.g. antimicrobial +
                # resistance) is stronger evidence than matching one broad
                # population or health term.
                score += 0.06
            if area_match:
                score += 0.03
            if domain_match:
                score += 0.05
            elif profile.disease_terms or profile.population_terms:
                score *= 0.70
            ethics_only = (
                bool(set(profile.population_terms) & PRODUCTION_ANIMALS)
                and bool(context_terms & ETHICS_HINTS)
                and not context_terms & {'poultry', 'livestock', 'veterinary'}
            )
            if ethics_only:
                # Ethics/philosophy journals can discuss animal welfare without
                # being a production-animal venue; keep them as exploratory,
                # not as the first answer for a poultry query.
                score *= 0.55
            evidence = (
                0.55 * focus_coverage
                + 0.20 * semantic_coverage
                + 0.15 * title_coverage
                + 0.10 * topic_coverage
            )
            if disease_match or population_match:
                evidence += 0.08
            if len(core_matches) >= 2:
                evidence += 0.04
            if domain_match:
                evidence += 0.04
            if not matched_focus:
                evidence *= 0.20
            elif method_only_match:
                evidence *= 0.45
            if ethics_only:
                evidence *= 0.80
        else:
            score = 0.65 * lexical_norm + 0.15 * semantic_coverage + 0.20 * (
                0.5 * title_coverage + 0.5 * topic_coverage
            )
            evidence = 0.55 * hit.coverage + 0.25 * title_coverage + 0.20 * topic_coverage
            if semantic_total:
                evidence += 0.10 * semantic_coverage

        evidence = max(0.0, min(1.0, evidence))
        label = _label(
            profile, evidence, focus_coverage, title_focus_count, topic_focus_count,
            matched_focus, method_only_match, hit.coverage, domain_match,
            population_match, disease_match,
        )
        reranked.append(RerankedHit(
            hit=hit,
            score=score,
            evidence=evidence,
            label=label,
            focus_coverage=focus_coverage,
            matched_focus=matched_focus,
            matched_methods=matched_methods,
            semantic_terms=matched_semantic,
            title_focus_count=title_focus_count,
            topic_focus_count=topic_focus_count,
            area_match=area_match,
            method_only_match=method_only_match,
            domain_match=domain_match,
        ))

    reranked.sort(key=lambda item: (-item.score, item.hit.index))
    return reranked[:max(1, int(top_k))]

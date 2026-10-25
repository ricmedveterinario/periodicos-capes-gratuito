"""Lightweight local semantic relatedness from catalogue topic co-occurrence.

This is a statistical method, not a neural sentence encoder. It learns which
canonical concepts tend to appear together in journal topics and uses that
signal only as a small bounded bonus during reranking. It requires no model
download, no external service and no additional dependency.

A compact multilingual sentence-transformer was deliberately not added: the
project has no torch/sentence-transformers installation, the model would add a
large download and memory footprint, and the statistical method below is the
baseline that must first show a measurable gain. See RECOMENDADOR.md for the
licence/size comparison and the negative/positive ablation result.
"""
from collections import Counter, defaultdict
from math import sqrt

from text_normalization import METHOD_TERMS


GENERIC_SEMANTIC = {
    'science', 'scientific', 'research', 'study', 'article', 'journal', 'review',
    'data', 'result', 'method', 'analysis', 'approach', 'paper', 'topic',
}


class TopicCooccurrenceModel:
    """Document-level co-occurrence model over journal topics.

    Terms that co-occur in many journal topic lists receive a small expansion
    weight. The model is intentionally conservative: minimum support and a
    minimum association threshold are required, and method terms are excluded
    so that a generic method cannot become a semantic bridge.
    """

    def __init__(self, index, min_support=3, min_association=0.10, top_n=4):
        self.index = index
        self.min_support = int(min_support)
        self.min_association = float(min_association)
        self.top_n = int(top_n)
        self.related = {}
        self._build()

    def _build(self):
        documents = []
        for position in range(len(self.index)):
            topics = self.index.field_terms['topics'][position]
            if not topics:
                topics = tuple(dict.fromkeys(
                    self.index.field_terms['title'][position]
                    + self.index.field_terms['scope'][position]
                ))
            terms = tuple(dict.fromkeys(
                term for term in topics
                if term not in METHOD_TERMS and term not in GENERIC_SEMANTIC
            ))
            if terms:
                documents.append(terms)

        document_frequency = Counter()
        pair_counts = defaultdict(int)
        for terms in documents:
            document_frequency.update(terms)
            for left_position, left in enumerate(terms):
                for right in terms[left_position + 1:]:
                    if left == right:
                        continue
                    pair_counts[tuple(sorted((left, right)))] += 1

        total = max(1, len(documents))
        candidates = defaultdict(list)
        for (left, right), count in pair_counts.items():
            if count < self.min_support:
                continue
            left_df = document_frequency[left]
            right_df = document_frequency[right]
            if not left_df or not right_df:
                continue
            # Cosine-like association, damped by support. It is less prone to
            # rewarding rare accidental pairs than raw PMI.
            association = count / sqrt(left_df * right_df)
            if association < self.min_association:
                continue
            candidates[left].append((right, association))
            candidates[right].append((left, association))

        for term, values in candidates.items():
            values.sort(key=lambda item: (-item[1], item[0]))
            self.related[term] = tuple(values[:self.top_n])

        self.document_frequency = document_frequency
        self.pair_counts = pair_counts

    def expand(self, terms, weight=0.12, max_per_term=2):
        """Return a bounded related-term map for a query concept set.

        With more than one query concept, a related term must be supported by
        at least two of them. This prevents a single ambiguous word such as
        ``welfare`` from pulling in an unrelated social-science vocabulary, or
        ``production`` from pulling in bioenergy vocabulary, when the rest of
        the manuscript points to a different domain.
        """
        terms = tuple(dict.fromkeys(terms))
        term_set = set(terms)
        support = {}
        for term in terms:
            for related, association in self.related.get(term, ())[:max_per_term]:
                if related in term_set or related in METHOD_TERMS or related in GENERIC_SEMANTIC:
                    continue
                count, best = support.get(related, (0, 0.0))
                support[related] = (count + 1, max(best, association))
        expansions = Counter()
        for related, (count, association) in support.items():
            if len(terms) > 1 and count < 2:
                continue
            share = count / len(terms)
            expansions[related] = max(
                expansions[related], weight * association * share
            )
        return expansions

    def related_terms(self, term, limit=4):
        return tuple(related for related, _ in self.related.get(term, ())[:limit])

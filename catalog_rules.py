"""Eligibility and institution rules shared by both recommender engines.

Eligibility is deliberately separate from thematic relevance. Nothing in this
module uses OpenAlex metrics or manuscript text.
"""
from text_normalization import clean


def institution_publishers(institutions, name):
    """Exact normalized institution name; never pool different substring matches."""
    found = institutions[institutions['Nome da Instituição'].map(clean) == clean(name)]
    publishers = set(found['Editora'].dropna())
    if 'Wiley' in publishers:
        publishers.update(['Wiley OnlineOpen', 'Wiley Gold'])
    return publishers


def integral_candidate(row):
    coverage = clean(row.get('Cobertura APC', ''))
    model = clean(row.get('Modelo', ''))
    blocked = ('pendente', 'sem publicacao', 'nao coberto', 'nao cobre', 'desconto', 'confirmar')
    return (row.get('Editora') != 'Wiley Gold' and not any(word in coverage for word in blocked)
            and 'subscription' not in model
            and (coverage == 'sim' or any(marker in coverage for marker in ('100%', 'integral', 'totalmente cobert', 'gratuito'))))

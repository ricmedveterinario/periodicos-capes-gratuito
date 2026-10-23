"""Explicit outbound research links; no scraping or manuscript upload."""
from urllib.parse import urlencode
from html import escape


OPENALEX_ABOUT = 'https://explore.openalex.org/about'


def scholar_journal_url(title):
    title = str(title).strip()[:500]
    return 'https://scholar.google.com/scholar?' + urlencode({'hl': 'pt-BR', 'as_publication': title})


def scholar_topic_url(topic):
    return 'https://scholar.google.com/scholar?' + urlencode({'hl': 'pt-BR', 'q': str(topic).strip()[:500]})


def summary_cards(total, with_metric, nature):
    values = [(total, 'Registros no catálogo'), (with_metric, 'Com métrica OpenAlex'),
              (nature, 'Títulos Nature'), (2, 'Modos de busca')]
    return '<div class="pa-summary">' + ''.join(
        '<div class="pa-summary-item"><strong>' + f'{int(value):,}'.replace(',', '.') +
        '</strong><span>' + escape(label) + '</span></div>' for value, label in values) + '</div>'

"""Institutional identity with official, bundled assets and no remote requests."""
import base64
from functools import lru_cache
from html import escape
from pathlib import Path


@lru_cache(maxsize=8)
def _asset(name):
    path = Path(__file__).parent / 'assets' / 'institutions' / name
    mime = 'image/svg+xml' if path.suffix == '.svg' else 'image/png'
    return 'data:' + mime + ';base64,' + base64.b64encode(path.read_bytes()).decode('ascii')


def _image(name, label, css=''):
    return (f'<img class="{escape(css)}" src="{_asset(name)}" '
            f'alt="{escape(label)}" decoding="async">')


def affiliation_html():
    return (
        '<nav class="pa-affiliations" aria-label="Instituições do projeto">'
        '<a href="https://www.ufu.br/" target="_blank" rel="noopener noreferrer" '
        'aria-label="Universidade Federal de Uberlândia — site oficial">'
        + _image('ufu.svg', 'UFU', 'pa-ufu-logo')
        + '<span>Universidade Federal<br>de Uberlândia</span></a>'
        '<a href="https://ppgcv.fmvz.ufu.br/" target="_blank" rel="noopener noreferrer" '
        'aria-label="PPGCVET — site oficial do Programa de Pós-graduação em Ciências Veterinárias">'
        + _image('ppgcvet.png', 'PPGCVET UFU', 'pa-program-logo')
        + '<span>Programa de Pós-graduação<br>em Ciências Veterinárias · FMVZ</span></a></nav>'
    )


def support_html():
    agencies = (
        ('capes.png', 'CAPES', 'Coordenação de Aperfeiçoamento de Pessoal de Nível Superior',
         'https://www.gov.br/capes/pt-br'),
        ('cnpq.png', 'CNPq', 'Conselho Nacional de Desenvolvimento Científico e Tecnológico',
         'https://www.gov.br/cnpq/pt-br'),
        ('fapemig.png', 'FAPEMIG', 'Fundação de Amparo à Pesquisa do Estado de Minas Gerais',
         'https://fapemig.br/'),
    )
    cards = ''.join(
        f'<a class="pa-support-card pa-support-{short.lower()}" href="{url}" '
        f'target="_blank" rel="noopener noreferrer" aria-label="{escape(short)} — site oficial">'
        f'<div class="pa-support-logo">{_image(file, short)}</div>'
        f'<span>{escape(name)}</span></a>'
        for file, short, name, url in agencies
    )
    return (
        '<section class="pa-support" aria-labelledby="pa-support-title">'
        '<div class="pa-section-label">AGRADECIMENTOS · APOIO À PESQUISA</div>'
        '<h2 id="pa-support-title">Ciência se faz em rede</h2>'
        '<p class="pa-support-intro">Agradecemos à CAPES, ao CNPq e à FAPEMIG pelo apoio '
        'à formação e à pesquisa, por meio de projetos e bolsas associados ao Grupo GOBIOTA '
        'no PPGCVET/FMVZ/UFU.</p>'
        f'<div class="pa-support-grid">{cards}</div>'
        '<p class="pa-support-note">As opiniões e recomendações desta ferramenta independente '
        'são de responsabilidade de seus autores e não necessariamente refletem a visão '
        'das instituições mencionadas.</p></section>'
    )

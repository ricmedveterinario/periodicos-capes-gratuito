"""Local, explainable thematic ranking. Manuscript text never leaves this process."""
from collections import Counter
from math import log
import re
import unicodedata

import pandas as pd


def clean(text):
    text = unicodedata.normalize('NFKD', str(text)).encode('ascii', 'ignore').decode().lower()
    return text


STOP = set('a an and are as at be by for from in is it of on or that the their this to was were with de da do das dos e em para por um uma os as que no na nos nas com estudo study studies results resultados methods metodo metodos conclusion conclusao journal international research revista'.split())
# Curated vocabulary expansion, not automatic translation or inferred journal scope.
GROUPS = [
    'veterinary veterinaria veterinario veterinarias veterinarios',
    'animal animals animais', 'microbiology microbiological microbiologia microbiano microbiana',
    'bacterial bacteria bacteriano bacteriana bacterias',
    'antimicrobial antimicrobiano antimicrobiana antimicrobianos antimicrobianas',
    'resistance resistant resistencia resistente', 'infection infections infectious infeccao infeccoes infecciosas infeccioso',
    'medicine medical medicina medico medica', 'health saude',
    'public publica publico', 'environment environmental ambiente ambiental',
    'ecology ecological ecologia ecologico ecologica', 'agriculture agricultural agricultura agricola',
    'food foods alimento alimentos alimentar', 'nutrition nutritional nutricao nutricional',
    'cancer oncology oncologia oncologico oncologica', 'immunology immunological imunologia imunologico imunologica',
    'genetics genetic genetica genetico genomics genomica',
    'biology biological biologia biologico biologica', 'molecular moleculares',
    'chemistry chemical quimica quimico', 'physics physical fisica fisico',
    'engineering engenharia', 'computer computing computacao computacional',
    'education educational educacao educacional', 'psychology psychological psicologia psicologico',
    'social sociais', 'economics economic economia economico',
    'surgery surgical cirurgia cirurgico', 'cardiology cardiovascular cardiologia',
    'neuroscience neurology neurologia neurociencia', 'epidemiology epidemiological epidemiologia epidemiologico',
    'parasitology parasitologia', 'virology virologia', 'reproduction reproductive reproducao reprodutivo',
    'aquaculture aquicultura', 'poultry avicultura', 'dairy leite lacteo',
    'water agua aguas', 'soil soils solo solos', 'plant plants planta plantas vegetal',
]
ALIASES = {word: group.split()[0] for group in GROUPS for word in group.split()}


def tokens(text):
    return [ALIASES.get(word, word) for word in re.findall(r'[a-z][a-z0-9]{2,}', clean(text)) if word not in STOP]


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


class JournalRecommender:
    def __init__(self, catalog):
        frames = []
        for publisher, frame in catalog.items():
            if publisher in {'INDICE', 'REQUISITOS', 'AVISOS'}:
                continue
            current = frame.copy()
            current['Editora'] = publisher
            frames.append(current)
        self.frame = pd.concat(frames, ignore_index=True).fillna('')
        fields = [c for c in self.frame if c == 'Título da Revista' or
                  clean(c) in {'area', 'area de conhecimento', 'subject area', 'subject', 'subjects', 'keywords', 'palavras-chave', 'area (openalex)', 'temas openalex'}]
        self.documents = [Counter(tokens(' '.join(str(row[c]) for c in fields)))
                          for _, row in self.frame.iterrows()]
        self.frequency = Counter(term for doc in self.documents for term in doc)
        self.lengths = [sum(doc.values()) for doc in self.documents]
        self.average_length = sum(self.lengths) / max(1, len(self.lengths)) or 1

    def recommend(self, title='', abstract='', keywords='', publishers=None, integral_only=True, limit=10):
        # Keywords and title have more weight than repeated words in a long abstract.
        query = Counter()
        for text, weight in [(title[:500], 3), (keywords[:1000], 4), (abstract[:12000], 1)]:
            for term in set(tokens(text)):
                query[term] += weight
        if not query or publishers == set():
            return self.frame.iloc[:0].copy()
        hits = []
        count = len(self.documents)
        for index, doc in enumerate(self.documents):
            row = self.frame.iloc[index]
            if publishers is not None and row['Editora'] not in publishers:
                continue
            if integral_only and not integral_candidate(row):
                continue
            matching = sorted(query.keys() & doc.keys())
            score = 0.0
            for term in matching:
                frequency = self.frequency[term]
                idf = log(1 + (count - frequency + 0.5) / (frequency + 0.5))
                tf = doc[term]
                score += query[term] * idf * tf * 2.5 / (tf + 1.5 * (0.25 + 0.75 * self.lengths[index] / self.average_length))
            if score > 0:
                hits.append((index, score, ', '.join(matching)))
        hits.sort(key=lambda hit: (-hit[1], str(self.frame.iloc[hit[0]]['Título da Revista']), str(self.frame.iloc[hit[0]]['Editora'])))
        selected = hits[:max(1, min(int(limit), 30))]
        result = self.frame.iloc[[hit[0] for hit in selected]].copy()
        result['Pontuação temática'] = [round(hit[1], 2) for hit in selected]
        result['Termos relacionados'] = [hit[2] for hit in selected]
        return result

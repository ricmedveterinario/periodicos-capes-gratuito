"""Join independently obtained OpenAlex CC0 metadata by exact ISSN."""
from pathlib import Path
import json
import gzip
import base64
import math
import re
from urllib.parse import urlparse

import pandas as pd
from journal_recommender import clean, integral_candidate, institution_publishers

METRIC = 'Média de citações em 2 anos (OpenAlex)'
H_INDEX = 'Índice h (OpenAlex)'
AREA = 'Área (OpenAlex)'
NO_AREA = 'Sem área identificada'
SNAPSHOT_PATH = Path(__file__).parent / 'data' / 'openalex_metrics.json.gz.b64'
FIELD_NAMES = {
    'Medicine': 'Medicina', 'Nursing': 'Enfermagem', 'Veterinary': 'Medicina veterinária',
    'Agricultural and Biological Sciences': 'Ciências agrárias e biológicas',
    'Biochemistry, Genetics and Molecular Biology': 'Bioquímica, genética e biologia molecular',
    'Immunology and Microbiology': 'Imunologia e microbiologia', 'Neuroscience': 'Neurociências',
    'Pharmacology, Toxicology and Pharmaceutics': 'Farmacologia e toxicologia',
    'Environmental Science': 'Ciências ambientais', 'Earth and Planetary Sciences': 'Ciências da Terra',
    'Physics and Astronomy': 'Física e astronomia', 'Chemistry': 'Química',
    'Chemical Engineering': 'Engenharia química', 'Engineering': 'Engenharia',
    'Materials Science': 'Ciência dos materiais', 'Energy': 'Energia',
    'Computer Science': 'Computação', 'Mathematics': 'Matemática',
    'Social Sciences': 'Ciências sociais', 'Arts and Humanities': 'Artes e humanidades',
    'Psychology': 'Psicologia', 'Economics, Econometrics and Finance': 'Economia e finanças',
    'Business, Management and Accounting': 'Negócios e gestão', 'Decision Sciences': 'Ciências da decisão',
    'Dentistry': 'Odontologia', 'Health Professions': 'Profissões da saúde',
    'Multidisciplinary': 'Multidisciplinar',
}


def issn_key(value):
    compact = re.sub(r'[^0-9X]', '', str(value).upper())
    if not re.fullmatch(r'\d{7}[\dX]', compact):
        return ''
    return compact


def safe_url(value):
    value = str(value or '').strip()
    parsed = urlparse(value)
    if parsed.scheme in {'https', 'http'} and parsed.netloc and not parsed.username and not parsed.password:
        return value
    return ''


def nonnegative(value):
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
        return number if math.isfinite(number) and number >= 0 else None
    except (ValueError, TypeError):
        return None


def read_snapshot(path=None):
    path = Path(path) if path else SNAPSHOT_PATH
    if not path.exists():
        return {'records': [], 'retrieved_at': '', 'license': 'CC0'}
    if path.suffix == '.b64':
        return json.loads(gzip.decompress(base64.b64decode(path.read_bytes())))
    if path.suffix == '.gz':
        with gzip.open(path, 'rt', encoding='utf-8') as stream:
            return json.load(stream)
    return json.loads(path.read_text(encoding='utf-8'))


def enrich_catalog(catalog, snapshot):
    index, ambiguous = {}, set()
    for record in snapshot['records']:
        for identifier in record.get('issns', []):
            key = issn_key(identifier)
            if not key:
                continue
            if key in index and index[key]['id'] != record['id']:
                ambiguous.add(key)
            index[key] = record
    frames = []
    for publisher, frame in catalog.items():
        if publisher in {'INDICE', 'REQUISITOS', 'AVISOS'}:
            continue
        frame = frame.copy()
        frame['Editora'] = publisher
        frames.append(frame)
    frame = pd.concat(frames, ignore_index=True).fillna('')
    metadata = []
    for _, row in frame.iterrows():
        key = issn_key(row.get('ISSN', ''))
        record = index.get(key, {}) if key not in ambiguous else {}
        stats = record.get('stats') or {}
        field = record.get('field') or ''
        metadata.append({
            METRIC: nonnegative(stats.get('2yr_mean_citedness')),
            H_INDEX: nonnegative(stats.get('h_index')),
            AREA: FIELD_NAMES.get(field, field) or NO_AREA,
            'Página da revista': safe_url(row.get('URL')) or safe_url(record.get('homepage')),
            'Fonte OpenAlex': safe_url(record.get('id')),
            'Consulta OpenAlex': snapshot.get('retrieved_at', '')[:10],
            'Correspondência': 'ISSN ambíguo; sem métrica' if key in ambiguous else ('ISSN exato' if record else 'Sem correspondência'),
            '_citation_history': record.get('history') or [],
            'Temas OpenAlex': '; '.join(record.get('topics') or [record.get('topic') or '']),
        })
    frame = pd.concat([frame, pd.DataFrame(metadata)], axis=1)
    for metric in (METRIC, H_INDEX):
        frame[metric] = pd.to_numeric(frame[metric], errors='coerce').astype(float)
    # Search journal metadata only; never search financial conditions as topic evidence.
    frame['_explorer_search'] = frame[['Título da Revista', 'ISSN', 'Editora', AREA]].astype(str).agg(' '.join, axis=1).map(clean)
    frame['_full_coverage'] = frame.apply(integral_candidate, axis=1)
    return frame


def filter_catalog(frame, query='', publishers=None, area=None, institutions=None, institution=None,
                   full_coverage=False, metric_only=False, minimum=0, order='Título'):
    result = frame
    for term in clean(query).split():
        if re.fullmatch(r'[\dXx-]{8,9}', term):
            target = issn_key(term)
            mask = result['ISSN'].map(issn_key) == target
        else:
            mask = result['_explorer_search'].str.contains(term, regex=False, na=False)
        result = result[mask]
    if publishers:
        result = result[result['Editora'].isin(publishers)]
    if area:
        result = result[result[AREA] == area]
    if institution and institutions is not None:
        allowed = institution_publishers(institutions, institution)
        result = result[result['Editora'].isin(allowed)]
    if full_coverage:
        result = result[result['_full_coverage']]
    if metric_only or minimum > 0:
        result = result[result[METRIC].notna() & (result[METRIC] >= minimum)]
    sort_column = {'Citações em 2 anos': METRIC, 'Índice h': H_INDEX}.get(order, 'Título da Revista')
    return result.sort_values([sort_column, 'Título da Revista'] if sort_column != 'Título da Revista' else [sort_column],
                              ascending=[False, True] if sort_column != 'Título da Revista' else True,
                              na_position='last', kind='stable').copy()


def chart_records(frame, metric=METRIC):
    # Multiple agreement rows can represent one journal; chart a journal once.
    frame = frame[frame[metric].notna()].drop_duplicates(subset=['ISSN'])
    records = []
    for _, row in frame.iterrows():
        records.append({
            'Revista': str(row['Título da Revista']), 'Editora': str(row['Editora']),
            'Área': row[AREA], 'Valor': float(row[metric]),
            'Página': safe_url(row['Página da revista']) or None, 'ISSN': str(row['ISSN']),
            'Faixa': sum(ord(char) for char in str(row['ISSN'])) % 9,
            'Consulta': row['Consulta OpenAlex'],
        })
    return records

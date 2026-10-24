"""Small, attributed Google Scholar Metrics pilot, never inferred from OpenAlex."""
from functools import lru_cache
from pathlib import Path
from html import escape
import json
import unicodedata

def title_key(value):
    return ' '.join(unicodedata.normalize('NFKC', str(value)).casefold().split())

@lru_cache(maxsize=1)
def snapshot():
    return json.loads((Path(__file__).parent/'data'/'scholar_metrics_pilot.json').read_text(encoding='utf-8'))

def lookup(title, data=None):
    data = snapshot() if data is None else data
    matches=[r for r in data['records'] if title_key(r['title'])==title_key(title)]
    return matches[0] if len(matches)==1 else None

def scholar_panel(title):
    data=snapshot(); record=lookup(title,data)
    if record is None:
        return ('<div style="border:1px solid #c7d2fe;border-left:4px solid #6366f1;background:#f8faff;border-radius:12px;padding:12px 16px;margin:14px 0">'
                '<strong style="color:#3730a3">Google Scholar · h5-index</strong>'
                '<div>Não disponível na nossa amostra de teste.</div>'
                '<div style="font-size:.875rem;color:#475569">Isso não significa que a revista não tenha índice no Google. O índice h do OpenAlex acima é outro indicador.</div></div>')
    h5, median=record['h5_index'],record['h5_median']
    if not all(type(v) is int and v>0 for v in (h5,median)) or median<h5:
        return ''
    direct = record.get('verification') == 'direct'
    provenance = ('Fonte: Google Scholar Metrics, conferido diretamente em ' + record.get('checked_at','') + '. Valores da edição indicada; não é atualização automática.'
                  if direct else 'Fonte: captura de 30/06/2026 preservada por ASSERT-KTH; conferida em 23/10/2026. Não é consulta ao vivo.')
    archive = ('' if direct else ' · <a target="_blank" rel="noopener noreferrer" href="'+escape(data['snapshot_url'],quote=True)+'">Ver captura de origem ↗</a>')
    return ('<div style="border:1px solid #c7d2fe;background:#eef2ff;border-radius:12px;padding:12px 16px;margin:10px 0">'
        '<strong style="color:#3730a3">Google Scholar Metrics · amostra de teste</strong>'
        f'<div style="display:flex;gap:24px;flex-wrap:wrap"><div>h5-index<br><strong style="font-size:1.875rem;color:#3730a3">{h5}</strong></div>'
        f'<div>h5-mediana<br><strong style="font-size:1.875rem;color:#3730a3">{median}</strong></div></div>'
        f'<div>Edição {data["edition"]} · artigos de {escape(data["period"])}</div>'
        '<div style="font-size:.875rem">h5-index e índice h do OpenAlex usam bases e períodos diferentes; não são equivalentes.</div>'
        '<div style="font-size:.875rem">'+escape(provenance)+'</div>'
        '<a target="_blank" rel="noopener noreferrer" href="'+escape(record['source_url'],quote=True)+'">Conferir no Google Scholar ↗</a>'+archive+'</div>')

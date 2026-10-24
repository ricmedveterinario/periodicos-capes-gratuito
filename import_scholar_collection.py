"""Offline import of a collection ZIP. Reads data only; never executes supplied code."""
import json
import re
import unicodedata
import zipfile
from pathlib import Path
from urllib.parse import urlparse, parse_qs

ALIASES = {
    '4OR': '4OR-A Quarterly Journal of Operations Research',
    'ACCESS IEEE Access': 'IEEE Access',
    'APMIS': 'APMIS. Acta pathologica, microbiologica et immunologica Scandinavica',
}

def normalized(title):
    text=unicodedata.normalize('NFKC',title).casefold().replace('&',' and ')
    return ' '.join(re.sub(r'[^\w]+',' ',text).split()).removeprefix('the ')

def same_title(title, confirmed):
    if normalized(title)==normalized(confirmed): return True
    if ALIASES.get(title)==confirmed: return True
    # Explicit publisher acronym suffix, never a generic subtitle or edition.
    match=re.fullmatch(r'(.+) \(([A-Z]{2,10})\)',confirmed)
    return bool(match and title.startswith('ACM ') and normalized(title)==normalized(match[1]))

def official_key(url):
    p=urlparse(url)
    if p.scheme!='https' or p.hostname!='scholar.google.com' or p.path!='/citations':
        raise ValueError('Invalid Google Scholar URL')
    q=parse_qs(p.query)
    if q.get('view_op')!=['list_hcore'] or len(q.get('venue',[]))!=1:
        raise ValueError('Invalid venue identifier')
    venue=q['venue'][0]
    if not venue.endswith('.2025'): raise ValueError('Unverified edition')
    return venue

def import_collection(zip_path, previous):
    with zipfile.ZipFile(zip_path) as z:
        records=json.loads(z.read('indice_H/dados/resultados_consolidados.json'))
        evidence={}
        for name in ['lote_00000_00200.json','top100_todas_areas.json']:
            batch=json.loads(z.read('indice_H/lotes/'+name))
            for item in batch['itens']:
                if item.get('status')!=200 or item.get('blocked') or item.get('error'): continue
                for row in item.get('rows',[]):
                    k=official_key(row['url'])
                    fact=(row['titulo'],int(row['h5']),int(row['med']))
                    if k in evidence and evidence[k]!=fact: raise ValueError('Conflicting raw evidence')
                    evidence[k]=fact
    old={official_key(r['source_url']):r for r in previous['records']}
    accepted=[]; seen=set(); rejected=[]
    for r in records:
        if r['status']!='confirmado': continue
        try:
            k=official_key(r['url_oficial'])
            if k in seen: raise ValueError('Duplicate venue')
            if r.get('validacao'): raise ValueError('Collection validation warning')
            if not same_title(r['titulo'],r['titulo_gs']): raise ValueError('Title requires review')
            if not all(type(r[x]) is int and r[x]>0 for x in ['h5','med']) or r['med']<r['h5']:
                raise ValueError('Invalid metric')
            if str(r['edicao'])!='2025': raise ValueError('Edition mismatch')
            if k in evidence:
                if evidence[k]!=(r['titulo_gs'],r['h5'],r['med']): raise ValueError('Raw evidence mismatch')
                verification='provided_collection'
            elif k in old and (old[k]['h5_index'],old[k]['h5_median'])==(r['h5'],r['med']):
                verification=old[k].get('verification','secondary')
            else: raise ValueError('No supporting batch or prior verified record')
            accepted.append({'title':r['titulo'],'issn':r['issn'],'google_title':r['titulo_gs'],
                'h5_index':r['h5'],'h5_median':r['med'],'source_url':r['url_oficial'],
                'edition':2025,'period':'2020–2024','checked_at':r['data'],
                'verification':verification,'snapshot_url':r.get('url_secundaria','')})
            seen.add(k)
        except ValueError as e: rejected.append({'title':r['titulo'],'reason':str(e)})
    return accepted,rejected

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('zip');p.add_argument('--output',required=True);p.add_argument('--report',required=True)
    args=p.parse_args(); output=Path(args.output)
    previous=json.loads(output.read_text(encoding='utf-8'))
    accepted,rejected=import_collection(args.zip,previous)
    report={'accepted':len(accepted),'rejected':rejected,'independent_live_recheck':False}
    Path(args.report).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    if rejected: raise SystemExit('Review rejected records before replacing snapshot')
    previous.update(records=accepted,checked_at='2026-10-24',provenance='Collection supplied by user; values validated against included batches and previous verified records. No live bulk recheck.')
    output.write_text(json.dumps(previous,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))

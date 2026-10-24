"""Count catalogue coverage independently of bibliometric availability."""
from journal_recommender import integral_candidate
from open_metrics import clean, issn_key

def catalog_counts(frame, google_lookup):
    full=frame.apply(integral_candidate,axis=1)
    partial=frame['Cobertura APC'].map(lambda v: '55%' in clean(v) or 'desconto' in clean(v)) & ~full
    linked=frame['Fonte OpenAlex'].map(lambda v: bool(str(v).strip()))
    google=sum(google_lookup(r['Título da Revista'],issn=r['ISSN']) is not None for _,r in frame.iterrows())
    return {'total':len(frame),'full':int(full.sum()),'partial':int(partial.sum()),
            'other':int((~full & ~partial).sum()),'openalex':int(linked.sum()),'google':google}

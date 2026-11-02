"""Deterministic, outcome-blinded time-support sample. No historical verdicts."""
from pathlib import Path
import hashlib,json
import numpy as np
import pandas as pd
from polaris_cliopatria import EXPECTED_HASHES
ROOT=Path(__file__).resolve().parents[1]
SEED='20261102-time-support-v1'
def rank(key):return hashlib.sha256((SEED+'|'+key).encode()).hexdigest()
def main():
    raw=ROOT/'data/raw/Polaris2026.xlsx'
    if hashlib.sha256(raw.read_bytes()).hexdigest()!=EXPECTED_HASHES['Polaris2026.xlsx']:raise ValueError('Polaris hash mismatch')
    folder=ROOT/'data/research50';x=pd.read_csv(folder/'feature_support_rows.csv');x=x[x.provenance.eq('polity_lifetime_display_assumption')].copy()
    registry=pd.read_excel(ROOT/'data/raw/Polaris2026.xlsx',sheet_name='Polities').set_index('polity_id')
    x=x[['polity_id','feature']].drop_duplicates();x['region']=x.polity_id.map(registry.seshat_region);x['start_year']=x.polity_id.map(registry.start_year);x['period']=pd.cut(x.start_year,[-np.inf,-500,1500,np.inf],labels=['before_500BCE','500BCE_to_1500CE','after_1500CE'],right=False).astype(str)
    # Take up to two unique polity-feature records per feature/period stratum.
    x['hash_rank']=[rank(a+'|'+b) for a,b in zip(x.polity_id,x.feature)];x=x.sort_values('hash_rank');selected=x.groupby(['feature','period'],observed=True,sort=True).head(2).sort_values(['feature','period','hash_rank'])
    fields=['polity_id','feature','region','start_year','period'];review=selected[fields].copy();review.insert(0,'review_id',[f'TS{i+1:03d}' for i in range(len(review))]);review['source_identifier']=review.polity_id+'|'+review.feature
    for col in ['reviewer','review_date','source_record_url','original_source_citation','source_text_or_page','explicit_time_start','explicit_time_end','time_support_verdict','construct_verdict','confidence','review_note']:review[col]=''
    out=ROOT/'research/review';out.mkdir(exist_ok=True);review.to_csv(out/'time_support_review.csv',index=False)
    (out/'sampling_manifest.json').write_text(json.dumps(dict(seed=SEED,sampling='two_hash_ranked_unique_polity_feature_records_per_feature_period_stratum',eligible_records=len(x),selected_records=len(review),features=review.feature.nunique(),period_counts=review.period.value_counts().to_dict(),selection_does_not_use=['area_outcome','model_score','false_positive','future_area'],limitations='stratified_audit_sample_not_population_error_estimator;sample_allows_repeated_polities;reviewers_must_not_consult_predictions'),indent=2)+'\n')
    print('Selected',len(review),'from',len(x),'unique polity-feature records')
if __name__=='__main__':main()

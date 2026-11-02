"""Coverage-only sensitivity to source site's displayed polity-date fallback.

No model is fitted and strict primary values are never replaced. The site's gray
fallback dates are a display convention, not independently dated measurements.
"""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
import pandas as pd
from polaris_cliopatria import FEATURES,EXPECTED_HASHES,feature_at,value
ROOT=Path(__file__).resolve().parents[1]

def fallback_at(records,year,start,end):
    """Only one unambiguous record and both dates null; retain source certainty.

    The website uses a broader year_from-null fallback. We deliberately do not
    overwrite partial explicit dates or resolve mixed dated/undated histories.
    """
    direct,status=feature_at(records,year,start,end)
    if np.isfinite(direct):return direct,'explicit_dated'
    if len(records)!=1:return np.nan,'not_single_source_record'
    row=records.iloc[0]
    if pd.notna(row.year_from) or pd.notna(row.year_to):return np.nan,'dated_or_partly_dated_not_extended'
    if bool(row.is_disputed) if pd.notna(row.is_disputed) else False:return np.nan,'disputed'
    if bool(row.is_uncertain) if pd.notna(row.is_uncertain) else False:return np.nan,'uncertain'
    if not start<=year<=end:return np.nan,'outside_polity'
    v=value(row)
    return v,'polity_lifetime_display_assumption' if np.isfinite(v) else 'uncertain_or_inferred_value'

def main():
    p=argparse.ArgumentParser();p.add_argument('--polaris-path',required=True);args=p.parse_args()
    if hashlib.sha256(Path(args.polaris_path).read_bytes()).hexdigest()!=EXPECTED_HASHES['Polaris2026.xlsx']:raise ValueError('Polaris hash mismatch')
    reg=pd.read_excel(args.polaris_path,sheet_name='Polities').set_index('polity_id');features=pd.read_excel(args.polaris_path,sheet_name='Social complexity');panel=pd.read_csv(ROOT/'data/research50/panel.csv');rows=[];summary=[]
    for pr in panel.itertuples():
        rr=reg.loc[pr.polity_id];fr=features[features.polity_id.eq(pr.polity_id)]
        for f in FEATURES:
            records=fr[fr.variable_name.eq(f)];v,status=fallback_at(records,pr.year,rr.start_year,rr.end_year)
            rows.append(dict(polity_id=pr.polity_id,year=pr.year,feature=f,strict_value=getattr(pr,f),fallback_sensitivity_value=v,provenance=status))
    out=ROOT/'data/research50';details=pd.DataFrame(rows)
    for f,g in details.groupby('feature',sort=False):summary.append(dict(feature=f,strict_nonmissing=int(g.strict_value.notna().sum()),fallback_sensitivity_nonmissing=int(g.fallback_sensitivity_value.notna().sum()),added_assumed_rows=int(g.provenance.eq('polity_lifetime_display_assumption').sum())))
    details.to_csv(out/'feature_support_rows.csv',index=False);pd.DataFrame(summary).to_csv(out/'feature_support_summary.csv',index=False)
    result=dict(status='coverage_sensitivity_only_no_models',candidate_rows=len(panel),strict_any_rows=int(details[details.strict_value.notna()][['polity_id','year']].drop_duplicates().shape[0]),fallback_any_rows=int(details[details.fallback_sensitivity_value.notna()][['polity_id','year']].drop_duplicates().shape[0]),source_site_commit='1f847d95e224860115a3dc358165380fe5487bcd',policy='single_undated_undisputed_certain_record_only;polity_date_display_not_independent_temporal_evidence',fitted_models=0)
    (out/'feature_support_manifest.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));print(pd.DataFrame(summary).to_string(index=False))
if __name__=='__main__':main()

"""Source-pinned, conservative exact-50-year feasibility audit, not a trained model.

No interpolation, forward fill, fuzzy identity match or missing-endpoint=collapse.
Only direct Cliopatria SeshatID -> Polaris polity_id mappings are accepted.
Undated / disputed / uncertain feature records are excluded from strict inputs.
"""
from pathlib import Path
import argparse,hashlib,io,json,urllib.request,zipfile
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
POLARIS_COMMIT='55ca5fbc2b563ddbbc1a3413071d4bd243d0a5fa'
CLIO_COMMIT='5f433377139a6eeaeacbdc894b70f8805b72c8b5'
SOURCES={
 'Polaris2026.xlsx':f'https://raw.githubusercontent.com/Seshat-Global-History-Databank/build_polaris_dataset/{POLARIS_COMMIT}/Polaris2026.xlsx',
 'cliopatria.geojson.zip':f'https://raw.githubusercontent.com/Seshat-Global-History-Databank/cliopatria/{CLIO_COMMIT}/cliopatria.geojson.zip'}
EXPECTED_HASHES={'Polaris2026.xlsx':'cf60c9f76eeda6db545521831a9201e65c64d2b74d4aeb55445cd2b564456c41','cliopatria.geojson.zip':'e10a4e429fca708788ff9e7572a95fce801fae55852d217cffabc1c59cd4eed4'}
# Fixed initial construct set, selected before expanded model fitting.
FEATURES=['polity_population','population_of_the_largest_settlement','administrative_level','military_level','full_time_bureaucrat','examination_system','merit_promotion','formal_legal_code','court','judge','professional_military_officer','professional_soldier','irrigation_system','road','food_storage_site','written_record','script','calendar','indigenous_coin','paper_currency']
BINARY={'P':1.,'A':0.}  # inferred/unknown codes remain missing, never absent.

def acquire(name):
    p=ROOT/'data/raw'/name;p.parent.mkdir(exist_ok=True,parents=True)
    if not p.exists():
        with urllib.request.urlopen(SOURCES[name],timeout=90) as r:p.write_bytes(r.read())
    return p,hashlib.sha256(p.read_bytes()).hexdigest()

def value(record):
    a=record.value_from;b=record.value_to
    if str(a) in BINARY:return BINARY[str(a)] if pd.isna(b) or str(b)==str(a) else np.nan
    try:
        a=float(a);b=float(b) if pd.notna(b) else a
    except (ValueError,TypeError):return np.nan
    # Do not silently collapse uncertain numerical ranges to point estimates.
    if not np.isfinite(a) or not np.isfinite(b) or a!=b:return np.nan
    return a

def area_at(records,year):
    rows=records[(records.FromYear<=year)&(records.ToYear>=year)]
    # Exactly one positive, POLITY geometry is needed. Multiple geometries
    # could be alternative extents/components; summing would invent a label.
    if len(rows)!=1:return np.nan,'missing' if rows.empty else 'ambiguous'
    a=float(rows.iloc[0].Area)
    return (a,'ok') if np.isfinite(a) and a>0 else (np.nan,'invalid_area')

def feature_at(records,year,polity_start,polity_end):
    if records.empty:return np.nan,'missing'
    dated=records.dropna(subset=['year_from','year_to'])
    dated=dated[(dated.year_from<=year)&(dated.year_to>=year)]
    dated=dated[~dated.is_disputed.fillna(False).astype(bool)&~dated.is_uncertain.fillna(False).astype(bool)]
    if len(dated)!=1:return np.nan,'missing_or_undated' if dated.empty else 'ambiguous'
    v=value(dated.iloc[0]);return v,'ok' if np.isfinite(v) else 'uncertain_value'

def connected_groups(registry,general,clio):
    """Conservative grouping for evaluation only, not a label continuity claim.

    Connect exact sourced predecessor/successor names and shared Cliopatria names.
    Larger groups err toward withholding related histories, not mixing them.
    Unmatched/ambiguous links logged, never guessed or accepted as labels.
    """
    ids=set(registry.polity_id);parent={i:i for i in ids};edges=[];unresolved=[]
    def find(x):
        while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
        return x
    def union(a,b,why):
        if a in ids and b in ids:parent[find(a)]=find(b);edges.append({'from_id':a,'to_id':b,'basis':why})
    names=registry.groupby('long_name').polity_id.agg(list).to_dict()
    for r in general[general.variable_name.isin(['polity_preceding_entity','polity_succeeding_entity'])].itertuples():
        candidates=names.get(str(r.value_from),[])
        if len(candidates)==1:union(r.polity_id,candidates[0],r.variable_name+':exact_registry_name')
        else:unresolved.append({'polity_id':r.polity_id,'relation':r.variable_name,'observed_name':str(r.value_from),'candidate_count':len(candidates)})
    for name,g in clio.groupby('Name'):
        members=sorted(set(g.SeshatID)&ids)
        for other in members[1:]:union(members[0],other,'shared_cliopatria_name:'+name)
    return {i:find(i) for i in ids},pd.DataFrame(edges),pd.DataFrame(unresolved)

def build(registry,clio,features,general,horizon=50):
    groups,edges,unresolved=connected_groups(registry,general,clio)
    candidates=[];excluded=[];coverage=[]
    for r in registry.itertuples():
        cr=clio[clio.SeshatID.eq(r.polity_id)&clio.Type.eq('POLITY')]
        if cr.empty:
            excluded.append(dict(polity_id=r.polity_id,year=np.nan,reason='no_direct_source_id_match'));continue
        # Uniform50-year marks, historical only. No modern-country outputs.
        for year in range(int(np.ceil(r.start_year/50)*50),min(int(r.end_year)-horizon,1900-horizon)+1,50):
            a,sa=area_at(cr,year);b,sb=area_at(cr,year+horizon)
            # Do not equate source-ID end with disappearance or use another ID
            # as successor without separate reviewed outcome continuity.
            if year+horizon>r.end_year:sb='outside_registry_end'
            if sa!='ok' or sb!='ok':
                excluded.append(dict(polity_id=r.polity_id,year=year,reason=f'current:{sa};future:{sb}'));continue
            ratio=b/a;outcome='decline' if ratio<=.7 else 'rise' if ratio>=1.3 else 'stable'
            prior,prior_status=area_at(cr,year-horizon)
            prior = prior if year-horizon>=r.start_year else np.nan
            row=dict(log_area_t=np.log10(a),log_area_prior=np.log10(prior) if np.isfinite(prior) else np.nan,past_log_area_change=np.log10(a/prior) if np.isfinite(prior) else np.nan,age_at_t=year-r.start_year,polity_id=r.polity_id,polity_name=r.long_name,year=year,target_year=year+horizon,group_id=groups[r.polity_id],area_t=a,area_future=b,area_ratio=ratio,outcome=outcome)
            fr=features[features.polity_id.eq(r.polity_id)]
            for f in FEATURES:
                row[f],status=feature_at(fr[fr.variable_name.eq(f)],year,r.start_year,r.end_year)
                coverage.append(dict(polity_id=r.polity_id,year=year,feature=f,status=status))
            candidates.append(row)
    return pd.DataFrame(candidates),pd.DataFrame(excluded),pd.DataFrame(coverage),edges,unresolved

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--polaris-path');parser.add_argument('--cliopatria-path');args=parser.parse_args()
    paths={};hashes={}
    for name,arg in [('Polaris2026.xlsx',args.polaris_path),('cliopatria.geojson.zip',args.cliopatria_path)]:
        if arg:p=Path(arg);h=hashlib.sha256(p.read_bytes()).hexdigest()
        else:p,h=acquire(name)
        if h!=EXPECTED_HASHES[name]:raise ValueError(f'Source hash mismatch: {name}')
        paths[name]=p;hashes[name]=h
    registry=pd.read_excel(paths['Polaris2026.xlsx'],sheet_name='Polities')
    general=pd.read_excel(paths['Polaris2026.xlsx'],sheet_name='General')
    features=pd.read_excel(paths['Polaris2026.xlsx'],sheet_name='Social complexity')
    with zipfile.ZipFile(paths['cliopatria.geojson.zip']) as z:
        names=[n for n in z.namelist() if n.endswith('.geojson')]
        if len(names)!=1:raise ValueError('Expected one GeoJSON')
        clio=pd.DataFrame([f['properties'] for f in json.loads(z.read(names[0]))['features']])
    out=ROOT/'data/research50';out.mkdir(exist_ok=True,parents=True)
    table,exclusions,coverage,edges,unresolved=build(registry,clio,features,general)
    table.to_csv(out/'panel.csv',index=False);exclusions.to_csv(out/'exclusions.csv',index=False)
    coverage.to_csv(out/'feature_coverage.csv',index=False);edges.to_csv(out/'grouping_edges.csv',index=False);unresolved.to_csv(out/'unresolved_grouping_links.csv',index=False)
    cols=['polity_id','long_name','start_year','end_year']
    registry[cols].merge(clio[['SeshatID','Name','FromYear','ToYear','Area','Type']],left_on='polity_id',right_on='SeshatID',how='left').to_csv(out/'direct_id_mapping.csv',index=False)
    summary=dict(status='feasibility_only_not_confirmatory_evidence',source_urls=SOURCES,sha256=hashes,horizon=50,target='decline_rise_stable_area_ratio',thresholds=[.7,1.3],registry_polities=len(registry),direct_id_matched_polities=registry.polity_id.isin(clio.SeshatID).sum().item(),candidate_rows=len(table),outcome_counts=table.outcome.value_counts().to_dict(),groups=table.group_id.nunique(),strict_feature_nonmissing={f:int(table[f].notna().sum()) for f in FEATURES},rows_with_any_strict_feature=int(table[FEATURES].notna().any(axis=1).sum()),missing_endpoint_rule='censored_not_collapse',lineage_status='conservative_sourced_grouping_not_verified_outcome_continuity',fitted_models=0)
    (out/'manifest.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()

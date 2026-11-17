"""Source/label sensitivity, no model selection or refitting.

Perturbation magnitudes are hypothetical stress tests, NOT estimated map error.
CrisisDB records are selected crisis annotations, NOT a negative-control cohort.
"""
import argparse,json,hashlib,zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from polaris_cliopatria import build,connected_groups,area_at,EXPECTED_HASHES
ROOT=Path(__file__).resolve().parents[1]
def read_clio(path):
    with zipfile.ZipFile(path) as z:
        names=[n for n in z.namelist() if n.endswith('.geojson') and not n.startswith('__MACOSX/')]
        if len(names)!=1:raise ValueError('Expected one GeoJSON')
        return pd.DataFrame([x['properties'] for x in json.loads(z.read(names[0]))['features']])
def classify(r):return 'decline' if r<=.7 else 'rise' if r>=1.3 else 'stable'
def possible_classes(lo,hi):
    return tuple(c for c,yes in [('decline',lo<=.7),('stable',hi>.7 and lo<1.3),('rise',hi>=1.3)] if yes)
def main():
    p=argparse.ArgumentParser();p.add_argument('--polaris-path',required=True);p.add_argument('--clio-path',required=True);p.add_argument('--previous-path',required=True);args=p.parse_args()
    expected_previous='d01ae3a20d358cc5d54f69d9d725d390767d9c8759ac89ad6f90c58d106f3370'
    prev_hash=hashlib.sha256(Path(args.previous_path).read_bytes()).hexdigest()
    if prev_hash!=expected_previous:raise ValueError('Previous source hash mismatch')
    for path,name in [(args.polaris_path,'Polaris2026.xlsx'),(args.clio_path,'cliopatria.geojson.zip')]:
        if hashlib.sha256(Path(path).read_bytes()).hexdigest()!=EXPECTED_HASHES[name]:raise ValueError(f'Current source hash mismatch: {name}')
    wb=pd.read_excel(args.polaris_path,sheet_name=None);reg=wb['Polities'];general=wb['General'];features=wb['Social complexity'];clio=read_clio(args.clio_path);previous=read_clio(args.previous_path)
    panel,exclusions,coverage,edges,unresolved=build(reg,clio,features,general);old,*_=build(reg,previous,features,general)
    out=ROOT/'data/research50';out.mkdir(parents=True,exist_ok=True)
    keys=['polity_id','year'];joined=panel[keys+['outcome','area_ratio']].merge(old[keys+['outcome','area_ratio']],on=keys,how='outer',suffixes=('_current','_previous'),indicator=True)
    joined['same_label']=joined.outcome_current.eq(joined.outcome_previous);joined.to_csv(out/'release_comparison_rows.csv',index=False)
    summary=[]
    for eps in [.05,.10,.20]:
        lo=panel.area_ratio*(1-eps)/(1+eps);hi=panel.area_ratio*(1+eps)/(1-eps)
        options=[possible_classes(a,b) for a,b in zip(lo,hi)];robust=np.array([len(x)==1 for x in options])
        for c in ['decline','rise','stable']:
            mask=panel.outcome.eq(c);summary.append(dict(test='hypothetical_independent_endpoint_area_error',magnitude=eps,outcome=c,rows=int(mask.sum()),invariant_rows=int((mask&robust).sum()),note='stress_test_not_empirical_uncertainty'))
    for shift in [1,10,25]:
        for c in ['decline','rise','stable']:
            total=0;ok=0
            for row in panel[panel.outcome.eq(c)].itertuples():
                cr=clio[clio.SeshatID.eq(row.polity_id)&clio.Type.eq('POLITY')];rr=reg[reg.polity_id.eq(row.polity_id)].iloc[0];labels=[]
                for delta in [-shift,0,shift]:
                    if row.year+delta<rr.start_year or row.target_year+delta>rr.end_year:labels.append('unavailable');continue
                    a,sa=area_at(cr,row.year+delta);b,sb=area_at(cr,row.target_year+delta);labels.append(classify(b/a) if sa==sb=='ok' else 'unavailable')
                total+=1;ok+=all(x==row.outcome for x in labels)
            summary.append(dict(test='hypothetical_calendar_shift',magnitude=shift,outcome=c,rows=total,invariant_rows=ok,note='not_dated_error_estimate_missing_shift_endpoint_is_noninvariant'))
    pd.DataFrame(summary).to_csv(out/'label_sensitivity_summary.csv',index=False)
    # Eligibility/selection at registry scale, without calling excluded states stable.
    registry=reg.copy();counts=panel.groupby('polity_id').size();registry['eligible_rows']=registry.polity_id.map(counts).fillna(0).astype(int);registry['direct_match']=registry.polity_id.isin(clio.SeshatID)
    registry.groupby('seshat_region').agg(registry_polities=('polity_id','size'),direct_matches=('direct_match','sum'),eligible_polities=('eligible_rows',lambda s:int(s.gt(0).sum())),eligible_rows=('eligible_rows','sum')).to_csv(out/'regional_selection.csv')
    # The last50years of lifespan fail the continuing-ID outcome policy by design.
    terminal=[]
    for rr in reg.itertuples():
        for t in range(int(np.ceil(rr.start_year/50)*50),min(int(rr.end_year),1850)+1,50):
            if t+50<=rr.end_year:continue
            cr=clio[clio.SeshatID.eq(rr.polity_id)&clio.Type.eq('POLITY')];a,status=area_at(cr,t)
            terminal.append(dict(polity_id=rr.polity_id,year=t,end_year=rr.end_year,current_geometry=status,source_relationship=';'.join(general.loc[general.polity_id.eq(rr.polity_id)&general.variable_name.eq('polity_relationship_to_preceding_entity'),'value_from'].dropna().astype(str)),review_status='censored_termination_not_inferred_collapse'))
    pd.DataFrame(terminal).to_csv(out/'terminal_window_review.csv',index=False)
    # Crisis records can flag agreement/disagreement; absence of a record is unlabelled.
    crisis=wb['CrisisDB - Crisis consequences'];matches=[]
    for r in panel.itertuples():
        found=crisis[(crisis.polity_id.eq(r.polity_id)|crisis.other_polity_id.eq(r.polity_id))&(crisis.year_from<=r.target_year)&(crisis.year_to>=r.year)]
        for cr in found.itertuples():matches.append(dict(polity_id=r.polity_id,year=r.year,area_outcome=r.outcome,crisis_owner=cr.polity_id,crisis_other=cr.other_polity_id,crisis_start=cr.year_from,crisis_end=cr.year_to,collapse_code=cr.collapse,decline_code=cr.decline,conquest_code=cr.conquest,interpretation='candidate_overlap_not_confirmed_endpoint_validation'))
    pd.DataFrame(matches).to_csv(out/'crisis_overlap_review.csv',index=False)
    # Check if explicit component/co-membership creates new connections not in splits.
    groups,_,_=connected_groups(reg,general,clio);name_ids=clio.groupby('Name').SeshatID.agg(lambda s:sorted(set(s)&set(reg.polity_id))).to_dict();extra=[]
    for r in clio.itertuples():
        ids=name_ids.get(r.Name,[])
        for field in ['Components','MemberOf']:
            for name in str(getattr(r,field,'')).split(';'):
                for a in ids:
                    for b in name_ids.get(name,[]):
                        if a!=b:extra.append(dict(a=a,b=b,basis=field+':'+r.Name+'|'+name,already_same_group=groups[a]==groups[b]))
    extra=pd.DataFrame(extra).drop_duplicates();extra.to_csv(out/'component_grouping_audit.csv',index=False)
    # Transitive paths through an ineligible registry polity also matter.
    parent={i:groups[i] for i in groups}
    def find(i):
        while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
        return i
    for rr in extra.itertuples():parent[find(rr.a)]=find(rr.b)
    strengthened={i:find(i) for i in groups};eligible_ids=set(panel.polity_id)
    changes=pd.DataFrame([dict(polity_id=i,old_group=groups[i],strengthened_group=strengthened[i],eligible=i in eligible_ids) for i in sorted(groups)])
    changes.to_csv(out/'strengthened_groups.csv',index=False)
    # Show all six source-coded collapse rows, including why the current panel misses them.
    collapse_review=[]
    for cr in crisis[crisis.collapse.eq('P')].itertuples():
        related=[i for i in [cr.polity_id,cr.other_polity_id] if isinstance(i,str)]
        for i in related:
            rr=reg[reg.polity_id.eq(i)]
            if rr.empty:continue
            rr=rr.iloc[0];mapped=clio[clio.SeshatID.eq(i)&clio.Type.eq('POLITY')]
            possible=panel[panel.polity_id.eq(i)]
            overlap=possible[(possible.year<=cr.year_to)&(possible.target_year>=cr.year_from)]
            collapse_review.append(dict(crisis_owner=cr.polity_id,related_polity=i,crisis_start=cr.year_from,crisis_end=cr.year_to,registry_start=rr.start_year,registry_end=rr.end_year,direct_geometry_records=len(mapped),eligible_rows=len(possible),overlapping_rows=len(overlap),reason='no_direct_id_geometry' if mapped.empty else 'no_eligible_overlap_under_strict_policy',review_status='source_annotation_only_not_independent_validation'))
    pd.DataFrame(collapse_review).to_csv(out/'direct_collapse_coverage.csv',index=False)
    result=dict(status='descriptive_adjudication_not_independent_expert_review',original_panel_groups=panel.group_id.nunique(),strengthened_panel_groups=len({strengthened[i] for i in eligible_ids}),current_rows=len(panel),previous_rows=len(old),common_rows=int(joined._merge.eq('both').sum()),changed_labels_common=int((joined._merge.eq('both')&~joined.same_label).sum()),current_only_rows=int(joined._merge.eq('left_only').sum()),previous_only_rows=int(joined._merge.eq('right_only').sum()),previous_sha256=prev_hash,terminal_windows=len(terminal),terminal_windows_with_current_geometry=sum(x['current_geometry']=='ok' for x in terminal),crisis_records=len(crisis),direct_present_collapse_records=int(crisis.collapse.eq('P').sum()),candidate_crisis_overlaps=len(matches),extra_component_edges=len(extra),extra_component_edges_crossing_existing_groups=int((~extra.already_same_group).sum()) if len(extra) else 0)
    (out/'adjudication_manifest.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));print(pd.DataFrame(summary).to_string(index=False))
if __name__=='__main__':main()

import importlib.util
from pathlib import Path
import numpy as np
import pandas as pd
p=Path(__file__).resolve().parents[1]/'research/polaris_cliopatria.py'
spec=importlib.util.spec_from_file_location('research50',p);r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)

def geometry():return pd.DataFrame([dict(FromYear=0,ToYear=99,Area=100.,SeshatID='a',Type='POLITY',Name='A'),dict(FromYear=100,ToYear=199,Area=50.,SeshatID='a',Type='POLITY',Name='A')])
def test_unique_interval_and_no_interpolation():
    x=geometry();assert r.area_at(x,50)==(100.,'ok');assert r.area_at(x,200)[1]=='missing'
    assert r.area_at(pd.concat([x,x]),50)[1]=='ambiguous'
    x.loc[0,'Area']=0;assert r.area_at(x,0)[1]=='invalid_area'
def test_feature_time_and_uncertainty():
    x=pd.DataFrame([dict(year_from=0,year_to=50,is_disputed=False,is_uncertain=False,value_from=1,value_to=1)])
    assert r.feature_at(x,25,0,200)==(1.,'ok');assert np.isnan(r.feature_at(x,100,0,200)[0])
    x.year_from=np.nan;assert np.isnan(r.feature_at(x,25,0,200)[0])
    x.year_from=0;x.is_uncertain=True;assert np.isnan(r.feature_at(x,25,0,200)[0])
    x.is_uncertain=False;x.value_to=2;assert np.isnan(r.feature_at(x,25,0,200)[0])
def test_binary_not_inferred_or_unknown():
    for code,v in [('P',1.),('A',0.),('IP',np.nan),('U',np.nan)]:
        got=r.value(pd.Series(dict(value_from=code,value_to=code)));assert got==v or (np.isnan(got) and np.isnan(v))
def test_binary_conflicting_endpoint_is_not_certain():
    assert np.isnan(r.value(pd.Series(dict(value_from='P',value_to='A'))))

def test_missing_endpoint_is_censored_and_prior_only():
    reg=pd.DataFrame([dict(polity_id='a',long_name='A',start_year=0,end_year=250)])
    f=pd.DataFrame(columns=['polity_id','variable_name','year_from','year_to','is_disputed','is_uncertain','value_from','value_to'])
    general=pd.DataFrame(columns=['polity_id','variable_name','value_from'])
    a,excluded,*_=r.build(reg,geometry(),f,general)
    assert len(a)==3 and set(a.year)=={0,50,100}
    assert 150 in set(excluded.year) and 200 in set(excluded.year)
    assert np.isnan(a.loc[a.year.eq(0),'log_area_prior'].iloc[0])
    changed=geometry();changed.loc[changed.FromYear.eq(100),'Area']=1
    b,*_=r.build(reg,changed,f,general)
    cols=['log_area_t','log_area_prior','past_log_area_change','age_at_t']
    np.testing.assert_equal(a.loc[a.year.eq(50),cols].to_numpy(),b.loc[b.year.eq(50),cols].to_numpy())
def test_grouping_is_source_based():
    reg=pd.DataFrame([dict(polity_id='a',long_name='A'),dict(polity_id='b',long_name='B')])
    general=pd.DataFrame([dict(polity_id='a',variable_name='polity_succeeding_entity',value_from='B')])
    groups,edges,unresolved=r.connected_groups(reg,general,geometry());assert groups['a']==groups['b'] and len(edges)==1

def test_sensitivity_boundaries():
    import sys
    sys.path.insert(0,str(p.parent))
    from adjudication_audit import possible_classes
    assert possible_classes(.7,.7)==('decline',)
    assert possible_classes(1.3,1.3)==('rise',)
    assert possible_classes(.8,1.2)==('stable',)
    assert possible_classes(.69,1.31)==('decline','stable','rise')

def test_source_display_sensitivity_never_replaces_partial_dates():
    import sys
    sys.path.insert(0,str(p.parent))
    from feature_support_audit import fallback_at
    x=pd.DataFrame([dict(year_from=np.nan,year_to=np.nan,is_disputed=False,is_uncertain=False,value_from='P',value_to=np.nan)])
    assert fallback_at(x,25,0,100)==(1.,'polity_lifetime_display_assumption')
    x.year_to=50;assert np.isnan(fallback_at(x,25,0,100)[0])
    x.year_to=np.nan;x.is_uncertain=True;assert np.isnan(fallback_at(x,25,0,100)[0])
    x.is_uncertain=False;x.value_from='IP';assert np.isnan(fallback_at(x,25,0,100)[0])
    x.value_from='P';assert np.isnan(fallback_at(pd.concat([x,x]),25,0,100)[0])

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from pipeline import FEATURES,CANDIDATES,build_table,MissingRateFilter,temporal_indices,load_source,ROOT,make_model,metrics

def fixture():
    d = pd.DataFrame({'NGA':['A']*4,'PolID':['X']*4,'Time':[0,100,200,300],'Terr':[2.,2.,1.,1.]})
    for f in FEATURES:d[f]=[1.,3.,9.,27.]
    return d

def test_delta_is_past_only():
    table=build_table(fixture())
    assert np.isnan(table.iloc[0].Pop_delta)
    assert table.iloc[1].Pop_delta == 2
    assert table.iloc[2].Pop_delta == 6

def test_future_feature_change_cannot_change_present_features():
    d=fixture(); first=build_table(d)
    d.loc[d.Time.eq(200),FEATURES]=9999
    second=build_table(d)
    pd.testing.assert_series_equal(first.iloc[1][CANDIDATES],second.iloc[1][CANDIDATES])

def test_labels_exact_and_censored():
    t=build_table(fixture())
    assert t.century.tolist()==[0,100,200]
    assert t.contraction.tolist()==[0,1,0]
    assert t.outcome.tolist()==['stable','decline','stable']
    assert build_table(fixture(),50).empty

def test_missingness_filter_fit_only_training():
    train=pd.DataFrame({'a':[1.,2.],'b':[np.nan,np.nan]})
    filt=MissingRateFilter().fit(train)
    assert list(filt.transform(pd.DataFrame({'a':[np.nan],'b':[1.]})))==['a']

def test_temporal_windows():
    d=pd.DataFrame({'century':[600,700,800,900]})
    tr,te=temporal_indices(d,800)
    assert tr.tolist()==[0] and te.tolist()==[2,3]

def test_group_exclusion_and_export_integrity():
    table=pd.read_parquet(ROOT/'data/table.parquet')
    splits=pd.read_csv(ROOT/'data/splits.csv')
    for key,s in splits[splits.protocol.eq('grouped')].groupby(['seed','fold']):
        train=table.iloc[s[s.partition.eq('train')].row]
        test=table.iloc[s[s.partition.eq('test')].row]
        assert set(train.group_id).isdisjoint(test.group_id)
    oof=pd.read_csv(ROOT/'data/oof.csv')
    assert len(oof)==len(table) and not oof.duplicated(['polity','century']).any()
    cases=pd.read_csv(ROOT/'data/fp_cases.csv')
    assert cases.oof_p_decline.ge(.7).all()
    assert (cases.true_label!='decline').all()

def test_shap_reconstructs_oof_log_odds():
    exp=pd.read_csv(ROOT/'dashboard/shap_long.csv')
    oof=pd.read_csv(ROOT/'data/oof.csv')
    for row,group in exp.groupby('row'):
        logit=group.shap_value.sum()+group.base_value.iloc[0]
        assert 1/(1+np.exp(-logit)) == pytest.approx(oof.iloc[row].p,abs=1e-8)

def test_model_preprocessing_and_missing_indicators():
    d=pd.DataFrame({f:[1.,2.,np.nan,4.,5.,6.] for f in CANDIDATES})
    model=make_model('logistic',0).fit(d,[0,0,0,1,1,1])
    assert any('missingindicator' in f for f in model.named_steps['imp'].get_feature_names_out())
    assert np.isfinite(model.predict_proba(d)).all()

def test_undefined_positive_ap():
    m=metrics([0,0],np.array([[.8,.2],[.9,.1]]),[0,1])
    assert np.isnan(m['ap_1'])

def test_streamlit_tabs_and_empty_case_handling():
    from streamlit.testing.v1 import AppTest
    app=AppTest.from_file(str(ROOT/'app.py')).run(timeout=20)
    assert not app.exception
    app.selectbox[0].select(app.selectbox[0].options[-1]).run()
    assert not app.exception

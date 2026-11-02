"""Interactive historical demo, using the exact OOF explanation exports."""
from pathlib import Path
import json
import pandas as pd
import streamlit as st
ROOT = Path(__file__).resolve().parent

@st.cache_data
def load_data():
    d = ROOT/'dashboard'
    return (pd.read_csv(d/'predictions.csv'),pd.read_csv(d/'shap_long.csv'),pd.read_csv(d/'fp_cases.csv',keep_default_na=False),pd.read_csv(d/'shap_groups.csv'),json.loads((d/'run_metadata.json').read_text()))

def main():
    st.set_page_config(page_title='Beyond the Empire',layout='wide')
    st.title('Beyond the Empire')
    st.caption('Equinox historical contraction explorer | 100-year exploratory baseline')
    st.warning('Uncalibrated model scores, not real-world risk probabilities. Only 6 observed contractions. No modern-country or causal claims.')
    try:
        data,explain,cases,groups,meta = load_data()
    except (FileNotFoundError,ValueError) as exc:
        st.error(f'Data unavailable: {exc}. Run python src/pipeline.py first.'); st.stop()
    a,b,c = st.columns(3)
    a.metric('Labeled observations',meta['rows'])
    b.metric('Observed contractions',meta['contractions'])
    c.metric('Confident false positives',len(cases))
    browser,audit,evaluation = st.tabs(['Polity browser','False-positive audit','Evaluation & limits'])
    with browser:
        polity = st.selectbox('Polity',sorted(data.polity.unique()))
        history = data[data.polity.eq(polity)].sort_values('time_t')
        time = st.selectbox('Observed year',history.time_t.tolist())
        selected = history[history.time_t.eq(time)].iloc[0]
        a,b = st.columns(2)
        a.metric('Out-of-fold contraction score',f'{selected.model_score:.3f}')
        b.metric('Observed next-century outcome',selected.outcome)
        st.caption('A polity is a historical political unit. A non-contraction is not proof of survival or protection from other crises.')
        st.line_chart(history.set_index('time_t')[['model_score']])
        explanation = explain[explain.polity.eq(polity)&explain.time_t.eq(time)]
        st.subheader('Why this held-out model gave this score')
        st.caption('Actual linear SHAP values from the training fold, in log-odds. Positive pushes toward contraction. These explain the model, not historical causes.')
        st.bar_chart(explanation.set_index('feature').shap_value)
        grouped = groups[groups.polity.eq(polity)&groups.time_t.eq(time)]
        st.bar_chart(grouped.set_index('feature_group').shap_value)
        st.dataframe(history[['time_t','Terr','next_Terr','outcome','model_score']],hide_index=True)
    with audit:
        st.subheader('Pre-specified rule: OOF score >= 0.70 and no observed contraction')
        st.info('Historical review is pending. No genuine_survival or label_artifact verdict is asserted without a source and review note.')
        if cases.empty:
            st.success('No cases meet this rule. No threshold was lowered to manufacture examples.')
        else:
            st.dataframe(cases,hide_index=True)
        st.download_button('Download review queue',cases.to_csv(index=False),'fp_cases.csv','text/csv')
        st.scatter_chart(data,x='time_t',y='model_score',color='contraction')
    with evaluation:
        st.write('Logistic regression, shallow random forest and training-fold majority baseline. Repeated grouped evaluation uses PolID across NGA, not a verified predecessor/successor lineage. Temporal holdout: year 800, with crossing label windows removed.')
        st.dataframe(pd.read_csv(ROOT/'data/fold_metrics.csv'),hide_index=True)
        st.write('Fold mean, standard deviation and valid-fold count:')
        st.dataframe(pd.read_csv(ROOT/'data/metrics_summary.csv',header=[0,1]))
        st.caption('Some folds contain no contractions. Their decline AP is undefined and omitted from the mean; the count column shows the valid folds. Repeated folds are correlated, not independent uncertainty intervals. The majority baseline wins grouped macro-F1 in this run.')
        st.write('Missingness removal, missing indicators, imputation and scaling are learned inside each training fold. The data cannot directly support an exact 50-year target; the CLI refuses to fabricate observations.')
        st.json(meta)
        st.download_button('Download predictions',data.to_csv(index=False),'predictions.csv','text/csv')

if __name__ == '__main__': main()

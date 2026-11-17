"""Interactive historical demo, using the exact OOF explanation exports."""
from pathlib import Path
import json
import pandas as pd
import streamlit as st
ROOT = Path(__file__).resolve().parent
if not (ROOT/'dashboard/run_metadata.json').exists():
    from src.bundled_exports import restore
    restore(ROOT)
AUDIT_THRESHOLD = 0.70

@st.cache_data
def load_data():
    d = ROOT/'dashboard'
    return (pd.read_csv(d/'predictions.csv'),pd.read_csv(d/'shap_long.csv'),pd.read_csv(d/'fp_cases.csv',keep_default_na=False),pd.read_csv(d/'shap_groups.csv'),json.loads((d/'run_metadata.json').read_text()))

@st.cache_data
def load_summary(path):
    s = pd.read_csv(path,header=[0,1],index_col=[0,1])
    s.columns = ['_'.join(c) for c in s.columns]
    return s.reset_index()

def main():
    st.set_page_config(page_title='Beyond the Empire',layout='wide')
    st.title('Beyond the Empire')
    st.caption('Equinox historical contraction explorer | 100-year exploratory baseline')
    st.warning('Uncalibrated model scores, not real-world risk probabilities. Only 6 observed contractions. No modern-country or causal claims.')
    with st.sidebar:
        st.header('How to read this')
        st.markdown('''- A **polity** is a historical political unit (state, kingdom, empire, city-state). Each row is one polity at one century.
- The **model score** is an out-of-fold logistic output: the row was held out when the model was fit. It is uncalibrated, so read it as a ranking signal, not a probability.
- **SHAP values** explain why the held-out model gave that score, in log-odds. Positive pushes toward contraction. They explain the model, not history.
- The audit flags every held-out row scoring **>= 0.70** whose observed outcome was not decline. All flagged cases await sourced historical review.''')
        st.caption('Source: pinned Equinox release. Full limits in docs/.')
    try:
        data,explain,cases,groups,meta = load_data()
    except (FileNotFoundError,ValueError) as exc:
        st.error(f'Data unavailable: {exc}. Run python src/pipeline.py first.'); st.stop()
    a,b,c,d4 = st.columns(4)
    a.metric('Labeled observations',meta['rows'])
    b.metric('Observed contractions',meta['contractions'])
    c.metric('Confident false positives',len(cases))
    summary = pd.read_csv(ROOT/'data/metrics_summary.csv',header=[0,1],index_col=[0,1])
    baseline = summary.loc[('grouped','majority'),('macro_f1','mean')]
    d4.metric('Majority baseline macro-F1',f'{baseline:.3f}',help='Grouped-fold mean. The models do not beat this baseline; see the Evaluation tab.')
    browser,audit,evaluation,research,whatif = st.tabs(['Polity browser','False-positive audit','Evaluation & limits','50-year research study','What-if (illustrative)'])
    with browser:
        polity = st.selectbox('Polity',sorted(data.polity.unique()))
        history = data[data.polity.eq(polity)].sort_values('time_t')
        time = st.selectbox('Observed year',history.time_t.tolist())
        selected = history[history.time_t.eq(time)].iloc[0]
        a,b = st.columns(2)
        a.metric('Out-of-fold contraction score',f'{selected.model_score:.3f}')
        b.metric('Observed next-century outcome',selected.outcome)
        st.caption('A polity is a historical political unit. A non-contraction is not proof of survival or protection from other crises.')
        st.subheader('Score and observed territory over time')
        st.caption(f'Top: out-of-fold score by century; the audit threshold is {AUDIT_THRESHOLD:.2f}. Bottom: observed log10 territory (Terr), the label source - never a model input.')
        trend = history.set_index('time_t')[['model_score']]
        st.line_chart(trend)
        st.line_chart(history.set_index('time_t')[['Terr']])
        explanation = explain[explain.polity.eq(polity)&explain.time_t.eq(time)].sort_values('shap_value')
        st.subheader('Why this held-out model gave this score')
        st.caption('Actual linear SHAP values from the training fold, in log-odds, sorted. Positive pushes toward contraction. These explain the model, not historical causes.')
        st.bar_chart(explanation.set_index('feature').shap_value)
        grouped = groups[groups.polity.eq(polity)&groups.time_t.eq(time)].sort_values('shap_value')
        st.bar_chart(grouped.set_index('feature_group').shap_value)
        st.dataframe(history[['time_t','Terr','next_Terr','outcome','model_score']],hide_index=True)
    with audit:
        st.subheader(f'Pre-specified rule: OOF score >= {AUDIT_THRESHOLD:.2f} and no observed contraction')
        st.info('Historical review is pending. No genuine_survival or label_artifact verdict is asserted without a source and review note.')
        if cases.empty:
            st.success('No cases meet this rule. No threshold was lowered to manufacture examples.')
        else:
            st.dataframe(cases,hide_index=True)
        st.download_button('Download review queue',cases.to_csv(index=False),'fp_cases.csv','text/csv')
        st.caption('Score versus observed outcome across all held-out rows. Points far above the threshold with no observed contraction are the audit queue.')
        st.scatter_chart(data,x='time_t',y='model_score',color='contraction')
    with evaluation:
        st.write('Logistic regression, shallow random forest and training-fold majority baseline. Repeated grouped evaluation uses PolID across NGA, not a verified predecessor/successor lineage. Temporal holdout: year 800, with crossing label windows removed.')
        st.dataframe(pd.read_csv(ROOT/'data/fold_metrics.csv'),hide_index=True)
        st.write('Fold mean, standard deviation and valid-fold count:')
        st.dataframe(load_summary(ROOT/'data/metrics_summary.csv'),hide_index=True)
        st.caption('Some folds contain no contractions. Their decline AP is undefined and omitted from the mean; the count column shows the valid folds. Repeated folds are correlated, not independent uncertainty intervals. The majority baseline wins grouped macro-F1 in this run.')
        st.write('Missingness removal, missing indicators, imputation and scaling are learned inside each training fold. This Equinox input cannot directly support an exact 50-year target; the CLI refuses to fabricate observations. The separate Polaris/Clio study is shown in the research tab.')
        st.json(meta)
        st.download_button('Download predictions',data.to_csv(index=False),'predictions.csv','text/csv')

    with research:
        st.subheader('Separate exploratory 50-year area-change study')
        st.warning('Not a governance or collapse predictor. This selected sample requires a continuing source ID and mapped future area. No publishability claim.')
        r=ROOT/'data/research50'
        if not (r/'manifest.json').exists():
            st.info('Research summaries unavailable. Run the commands in research/README.md.')
        else:
            rm=json.loads((r/'manifest.json').read_text())
            a,b,c=st.columns(3)
            a.metric('Candidate observations',rm['candidate_rows'])
            b.metric('Decline observations',rm['outcome_counts']['decline'])
            c.metric('Rows with any strict governance/scale feature',rm['rows_with_any_strict_feature'])
            st.write('756 rows are repeated historical reconstructions, not 756 independent events. Declines occur in only 30 conservative linked groups. The strict governance coverage is too sparse for the intended broad governance model.')
            st.subheader('Area-history model evaluation')
            st.caption('Inputs: current area, prior area, past area change and historical age. Grouped: five folds across three seeds. Temporal holdout also excludes test groups from training.')
            st.dataframe(load_summary(r/'area_history_summary.csv'),hide_index=True)
            st.write('Time-plus-group holdout macro-F1: forest 0.287, majority 0.285, logistic 0.226. This does not establish a useful improvement.')
            st.dataframe(pd.read_csv(r/'area_history_bootstrap.csv'),hide_index=True)
            st.caption('Seed 0 pooled OOF paired group-bootstrap descriptive intervals include zero. They are conditional on this selected sample, not confirmatory uncertainty intervals.')
            st.subheader('Strict temporal feature coverage')
            st.dataframe(pd.read_csv(r/'strict_feature_summary.csv'),hide_index=True)
            st.write('Undated, disputed, uncertain or ambiguous values remain missing. Missing endpoints are censored, never called collapse or stable. Boundary uncertainty and source continuity still require historical review.')
            st.download_button('Download expanded evaluation summary',(r/'area_history_summary.csv').read_bytes(),'area_history_summary.csv','text/csv')
            st.markdown('Protocol and full limits: `research/protocol.md`, `docs/research_findings.md`. Reproduction: `research/README.md`. These summaries never replace the Equinox dashboard predictions.')
            st.json(rm)

    with whatif:
        st.subheader('Illustrative what-if score')
        st.warning('Non-causal and illustrative only. The logistic baseline is fitted on all 98 labelled observations for exploration; the output is an uncalibrated model score, not a probability of collapse, and it must not be read as a historical or modern claim.')
        @st.cache_resource
        def fit_whatif():
            from src.pipeline import make_model, CANDIDATES
            table = pd.read_parquet(ROOT/'data/table.parquet')
            model = make_model('logistic', 0)
            model.fit(table[CANDIDATES], table.contraction)
            medians = table[CANDIDATES].median(numeric_only=True)
            return table, model, medians
        try:
            wtable, wmodel, wmedians = fit_whatif()
        except Exception as exc:
            st.error(f'What-if model unavailable: {exc}')
        else:
            cases = (wtable.polity + ' @ ' + wtable.century.astype(int).astype(str)).tolist()
            default_ix = int((wtable.polity.eq('Latium::ItRomPr') & wtable.century.eq(100)).idxmax())
            choice = st.selectbox('Prefill from a real labelled polity-century', cases, index=default_ix)
            row = wtable.iloc[cases.index(choice)]
            st.caption('Inputs start from the selected real observation. Where the historical record is missing, the input starts at the training median - the same value the pipeline median-imputer would supply. Adjust any of the 14 model inputs.')
            from src.pipeline import FEATURES, CANDIDATES
            labels = {f'{f}_delta': f'{f} change over prior century' for f in FEATURES}
            values = {}
            cols = st.columns(2)
            for i, feat in enumerate(CANDIDATES):
                raw = row[feat]
                imputed = pd.isna(raw)
                start = float(wmedians[feat]) if imputed else float(raw)
                values[feat] = cols[i % 2].number_input(
                    labels.get(feat, feat) + (' (median-filled)' if imputed else ''),
                    value=start, key=f'whatif_{feat}')
            if st.button('Compute illustrative score'):
                import numpy as np
                X = pd.DataFrame([values], columns=CANDIDATES)
                score = float(wmodel.predict_proba(X)[0, 1])
                st.metric('Illustrative contraction-warning score', f'{score:.3f}')
                st.caption('Same median-imputation and standardization pipeline as the audited baseline. A higher score only means the inputs look more like labelled contractions to this small logistic model. It is not a validated risk estimate.')

if __name__ == '__main__': main()

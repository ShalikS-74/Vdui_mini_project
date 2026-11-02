"""Reproducible Equinox exploration. Scores are not calibrated risks."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import urllib.request
import warnings
import numpy as np
import pandas as pd
import shap
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, f1_score, precision_score, recall_score
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
FEATURES = ['Pop', 'Cap', 'Hier', 'Gov', 'Infra', 'Info', 'Money']
CANDIDATES = FEATURES + [f'{f}_delta' for f in FEATURES]
SOURCE_COMMIT = '602c7cdf0649e1fbbdb37f5b5a387edbe19915d0'
SOURCE_URL = f'https://raw.githubusercontent.com/seshatdb/Equinox_Data/{SOURCE_COMMIT}/Equinox_on_GitHub_June9_2022.xlsx'
THRESHOLD = .7

class MissingRateFilter(TransformerMixin, BaseEstimator):
    """Feature removal is learned on TRAINING rows only, never global data."""
    def __init__(self, max_missing=.6):
        self.max_missing = max_missing
    def fit(self, X, y=None):
        self.columns_ = X.columns[X.isna().mean() <= self.max_missing].tolist()
        if not self.columns_:
            raise ValueError('No features pass the training-fold missingness rule')
        return self
    def transform(self, X):
        return X[self.columns_]
    def get_feature_names_out(self, input_features=None):
        return np.asarray(self.columns_, dtype=object)

def source_file():
    path = ROOT / 'data/raw/Equinox_on_GitHub_June9_2022.xlsx'
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        with urllib.request.urlopen(SOURCE_URL, timeout=60) as response:
            path.write_bytes(response.read())
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return path, digest

def load_source(path):
    frame = pd.read_excel(path, sheet_name='AggrSCWarAgriRelig').replace(-999, np.nan)
    frame = frame[frame['uniq'].astype(str).str.lower().ne('n')].copy()
    for col in ['Time', 'Terr'] + FEATURES:
        frame[col] = pd.to_numeric(frame[col], errors='coerce')
    if frame[['NGA', 'PolID', 'Time']].isna().any().any():
        raise ValueError('Missing observation key')
    if frame.duplicated(['NGA', 'PolID', 'Time']).any():
        raise ValueError('Duplicate observation keys; resolve explicitly before joining')
    return frame.sort_values(['NGA', 'PolID', 'Time']).reset_index(drop=True)

def build_table(frame, horizon=100, target='binary'):
    if horizon <= 0:
        raise ValueError('horizon must be positive')
    keys = ['NGA', 'PolID', 'Time']
    now = frame[keys + FEATURES + ['Terr']].copy()
    future = now[keys + ['Terr']].rename(columns={'Time': 'next_time', 'Terr': 'next_Terr'})
    panel = now.assign(next_time=now.Time + horizon).merge(future, on=['NGA', 'PolID', 'next_time'], how='left', validate='one_to_one')
    # A source observation at s is moved to merge key s+H. A row at t
    # therefore receives s=t-H, NEVER t+H. The original audit reversed this.
    past = now[keys + FEATURES].copy()
    past['Time'] += horizon
    past = past.rename(columns={f: f'{f}_previous' for f in FEATURES})
    panel = panel.merge(past, on=keys, how='left', validate='one_to_one')
    for f in FEATURES:
        panel[f'{f}_delta'] = panel[f] - panel[f'{f}_previous']
    panel = panel.dropna(subset=['Terr', 'next_Terr']).copy()
    change = panel.next_Terr - panel.Terr
    panel['contraction'] = (change <= np.log10(.7)).astype(int)
    panel['outcome'] = np.select([change <= np.log10(.7), change >= np.log10(1.3)], ['decline', 'rise'], default='stable')
    panel['polity'] = panel.NGA + '::' + panel.PolID
    # Conservative observed polity identifier across NGA. This is NOT an
    # invented predecessor/successor lineage; see scope and continuity reports.
    panel['group_id'] = panel.PolID
    panel = panel.rename(columns={'NGA': 'nga', 'Time': 'century'})
    return panel[['nga','PolID','polity','group_id','century','next_time','Terr','next_Terr','contraction','outcome'] + CANDIDATES].sort_values(['polity','century']).reset_index(drop=True)

def make_model(kind, seed):
    models = {
        'logistic': LogisticRegression(class_weight='balanced', max_iter=3000, random_state=seed),
        'forest': RandomForestClassifier(n_estimators=150, max_depth=3, min_samples_leaf=4, class_weight='balanced', random_state=seed, n_jobs=1),
        'majority': DummyClassifier(strategy='prior'),
    }
    return Pipeline([('filter', MissingRateFilter()), ('imp', SimpleImputer(strategy='median', add_indicator=True, keep_empty_features=True)), ('scale', StandardScaler()), ('model', models[kind])])

def metrics(y, p, classes):
    result = {'macro_f1': f1_score(y, np.asarray(classes)[p.argmax(axis=1)], labels=classes, average='macro', zero_division=0)}
    for i, cls in enumerate(classes):
        positives = np.asarray(y) == cls
        # No positive examples means AP is undefined, not zero performance.
        result[f'ap_{cls}'] = average_precision_score(positives, p[:,i]) if positives.any() else np.nan
    return result

def temporal_indices(table, cutoff, horizon=100):
    return np.flatnonzero(table.century + horizon < cutoff), np.flatnonzero(table.century >= cutoff)

def run_evaluation(table, target='binary', horizon=100):
    y = table.contraction.to_numpy() if target == 'binary' else table.outcome.to_numpy()
    classes = np.unique(y)
    if len(classes) < 2:
        raise ValueError('Insufficient observed target classes for evaluation')
    predictions, memberships, scores, explanations = [], [], [], []
    tasks = []
    for seed in [0,1,2]:
        cv = StratifiedGroupKFold(n_splits=min(5,table.group_id.nunique()), shuffle=True, random_state=seed)
        for fold, (train,test) in enumerate(cv.split(table[CANDIDATES], y, table.group_id)):
            assert set(table.iloc[train].group_id).isdisjoint(table.iloc[test].group_id)
            tasks.append(('grouped',seed,fold,train,test))
    tr,te = temporal_indices(table,800,horizon)
    tasks.append(('temporal',0,0,tr,te))
    for protocol,seed,fold,train,test in tasks:
        for partition, indices in [('train',train),('test',test)]:
            memberships.extend(dict(protocol=protocol,seed=seed,fold=fold,row=int(i),partition=partition) for i in indices)
        if not len(test) or len(np.unique(y[train])) < 2:
            scores.append(dict(protocol=protocol,seed=seed,fold=fold,model='all',status='skipped: empty test or single-class train'))
            continue
        for kind in ['logistic','forest','majority']:
            model = make_model(kind,seed).fit(table.iloc[train][CANDIDATES], y[train])
            raw = model.predict_proba(table.iloc[test][CANDIDATES])
            fitted_classes = model.named_steps['model'].classes_
            p = np.zeros((len(test),len(classes)))
            for i,cls in enumerate(fitted_classes):
                p[:,list(classes).index(cls)] = raw[:,i]
            scores.append(dict(protocol=protocol,seed=seed,fold=fold,model=kind,status='ok',n_train=len(train),n_test=len(test),**metrics(y[test],p,classes)))
            for j,index in enumerate(test):
                predictions.append(dict(protocol=protocol,seed=seed,fold=fold,model=kind,row=int(index),y=y[index],**{f'score_{cls}':p[j,i] for i,cls in enumerate(classes)}))
            # Fold-specific SHAP for the exact logistic model that generated
            # the displayed OOF score. Binary SHAP is additive in log-odds.
            if target == 'binary' and kind == 'logistic' and protocol == 'grouped' and seed == 0:
                train_z = model[:-1].transform(table.iloc[train][CANDIDATES])
                test_z = model[:-1].transform(table.iloc[test][CANDIDATES])
                names = model.named_steps['imp'].get_feature_names_out(model.named_steps['filter'].columns_)
                explainer = shap.LinearExplainer(model.named_steps['model'], train_z)
                values = explainer(test_z)
                assert np.allclose(values.values.sum(axis=1)+values.base_values, model.decision_function(table.iloc[test][CANDIDATES]))
                for j,index in enumerate(test):
                    for k,feature in enumerate(names):
                        explanations.append(dict(row=int(index),polity=table.iloc[index].polity,time_t=int(table.iloc[index].century),feature=feature,value=float(test_z[j,k]),shap_value=float(values.values[j,k]),base_value=float(values.base_values[j]),fold=fold,units='log_odds',model='logistic_oof_seed0'))
    return pd.DataFrame(predictions),pd.DataFrame(memberships),pd.DataFrame(scores),pd.DataFrame(explanations)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--target', choices=['binary','three-class'], default='binary')
    parser.add_argument('--horizon', type=int, default=100)
    args = parser.parse_args()
    path,digest = source_file()
    raw = load_source(path)
    table = build_table(raw,args.horizon,args.target)
    if table.empty:
        raise SystemExit('No exact future observations at requested horizon. No interpolated or invented labels produced.')
    out = ROOT / 'data' if args.target == 'binary' and args.horizon == 100 else ROOT / f'data/{args.target}-{args.horizon}'
    out.mkdir(parents=True,exist_ok=True)
    raw[FEATURES].isna().mean().rename('missing_rate').to_csv(out/'missingness.csv')
    table[['polity','PolID','group_id']].drop_duplicates().assign(lineage_status='observed_polity_only_not_verified_lineage').to_csv(out/'continuity.csv',index=False)
    table.to_parquet(out/'table.parquet',index=False)
    pred,splits,folds,explain = run_evaluation(table,args.target,args.horizon)
    pred.to_csv(out/'split_predictions.csv',index=False)
    splits.to_csv(out/'splits.csv',index=False)
    folds.to_csv(out/'fold_metrics.csv',index=False)
    numeric = [c for c in folds if c.startswith('ap_') or c == 'macro_f1']
    summary = folds.groupby(['protocol','model'])[numeric].agg(['mean','std','count'])
    summary.to_csv(out/'metrics_summary.csv')
    metadata = dict(source_url=SOURCE_URL,source_sha256=digest,source_commit=SOURCE_COMMIT,horizon=args.horizon,target=args.target,rows=len(table),class_counts=table.outcome.value_counts().to_dict(),contractions=int(table.contraction.sum()),grouping='PolID, not verified lineage',fp_threshold=THRESHOLD,score='uncalibrated',seeds=[0,1,2],temporal_cutoff=800)
    (out/'run_metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
    if args.target != 'binary' or args.horizon != 100:
        print(summary.to_string()); return
    oof = pred.query("protocol == 'grouped' and seed == 0 and model == 'logistic'").set_index('row').sort_index()
    assert len(oof) == len(table) and oof.index.is_unique
    data = table.copy()
    data['p'] = oof.score_1.to_numpy()
    data['y'] = data.contraction
    data['fp_flag'] = ((data.p >= THRESHOLD) & data.y.eq(0)).astype(int)
    data.to_csv(out/'oof.csv',index=False)
    cases = data.loc[data.fp_flag.eq(1),['polity','century','p','outcome','fp_flag']].rename(columns={'p':'oof_p_decline','outcome':'true_label'})
    # Never replace authored review evidence on regeneration.
    review_path = ROOT/'data/manual_reviews.csv'
    if review_path.exists():
        reviews = pd.read_csv(review_path,keep_default_na=False)
        if reviews.duplicated(['polity','century']).any(): raise ValueError('Duplicate manual reviews')
        allowed = {'pending','genuine_survival','label_artifact','unresolved'}
        if not set(reviews['type']).issubset(allowed): raise ValueError('Invalid review type')
        verified = reviews['type'].isin(['genuine_survival','label_artifact'])
        if (reviews.loc[verified,'source_url'].eq('') | reviews.loc[verified,'note'].eq('')).any(): raise ValueError('Historical verdict requires source and note')
        cases = cases.merge(reviews,on=['polity','century'],how='left',validate='one_to_one')
    for col,default in [('type','pending'),('note','Historical review not completed; no protective-factor claim.'),('source_url','')]:
        if col not in cases: cases[col]=default
        cases[col] = cases[col].fillna(default)
    cases.to_csv(out/'fp_cases.csv',index=False)
    explain.to_csv(out/'shap_long.csv',index=False)
    fp_ids = data.index[data.fp_flag.eq(1)]
    tp_ids = data.index[(data.p >= THRESHOLD)&data.y.eq(1)]
    ranking = explain.groupby('feature').apply(lambda g: pd.Series({'fp_mean_shap':g[g.row.isin(fp_ids)].shap_value.mean(),'tp_mean_shap':g[g.row.isin(tp_ids)].shap_value.mean()}),include_groups=False)
    ranking['difference'] = ranking.fp_mean_shap-ranking.tp_mean_shap
    ranking.to_csv(out/'fp_feature_ranking.csv')
    dashboard = ROOT/'dashboard'
    data.rename(columns={'century':'time_t','p':'model_score'}).to_csv(dashboard/'predictions.csv',index=False)
    for filename in ['shap_long.csv','fp_cases.csv','fold_metrics.csv','metrics_summary.csv','run_metadata.json']:
        shutil.copyfile(out/filename,dashboard/filename)
    groups = {'Pop':'scale','Cap':'scale','Hier':'administration','Gov':'governance','Infra':'infrastructure','Info':'information','Money':'monetary_system'}
    explain['feature_group'] = explain.feature.str.removeprefix('missingindicator_').str.removesuffix('_delta').map(groups)
    explain.groupby(['row','polity','time_t','feature_group'],dropna=False).shap_value.sum().reset_index().to_csv(dashboard/'shap_groups.csv',index=False)
    print(summary.to_string())
    print(f'Rows={len(table)}; contractions={table.contraction.sum()}; confident FP={len(cases)}; all pending sourced historical review')

if __name__ == '__main__': main()

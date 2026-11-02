"""Retrospective display-scenario evaluation; see secondary_protocol.md."""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import f1_score,average_precision_score
ROOT=Path(__file__).resolve().parents[1]
FEATURES=['log_area_t','log_area_prior','past_log_area_change','age_at_t']
CLASSES=['decline','rise','stable']
def model(kind,seed):
    estimator={'majority':DummyClassifier(strategy='most_frequent'),'logistic':LogisticRegression(C=1,class_weight='balanced',max_iter=3000,random_state=seed),'forest':RandomForestClassifier(n_estimators=150,max_depth=3,min_samples_leaf=4,class_weight='balanced',random_state=seed,n_jobs=1)}[kind]
    return make_pipeline(SimpleImputer(strategy='median',add_indicator=True,keep_empty_features=True),StandardScaler(),estimator)
def metrics(y,p):
    r={'macro_f1':f1_score(y,np.array(CLASSES)[p.argmax(axis=1)],labels=CLASSES,average='macro',zero_division=0)}
    for i,c in enumerate(CLASSES):r['ap_'+c]=average_precision_score(np.array(y)==c,p[:,i]) if (np.array(y)==c).any() else np.nan
    return r

def main():
    out=ROOT/'data/research50';table=pd.read_csv(out/'panel.csv');support=pd.read_csv(out/'feature_support_rows.csv');gov=support.pivot(index=['polity_id','year'],columns='feature',values='fallback_sensitivity_value');gov=gov.reindex(pd.MultiIndex.from_frame(table[['polity_id','year']])).reset_index(drop=True);area=table[FEATURES].reset_index(drop=True);y=table.outcome;g=table.group_id;X=area
    predictions=[];folds=[];members=[]
    splits=[]
    membership=pd.read_csv(out/'area_history_split_membership.csv')
    for (protocol,seed,fold),m in membership.groupby(['protocol','seed','fold']):
        tr=m.loc[m.partition.eq('train'),'row'].to_numpy();te=m.loc[m.partition.eq('test'),'row'].to_numpy();assert set(g.iloc[tr]).isdisjoint(g.iloc[te]);splits.append((protocol,int(seed),int(fold),tr,te))
    for protocol,seed,fold,tr,te in splits:
        for partition,indices in [('train',tr),('test',te)]:members.extend({'protocol':protocol,'seed':seed,'fold':fold,'row':int(i),'partition':partition} for i in indices)
        if len(np.unique(y.iloc[tr]))<3 or not len(te):
            folds.append(dict(protocol=protocol,seed=seed,fold=fold,model='all',status='insufficient_training_classes_or_empty_test'));continue
        for experiment in ['governance_only_logistic','governance_only_forest','combined_logistic','combined_forest']:
            kind=experiment.split('_')[-1];X=gov if experiment.startswith('governance_only') else pd.concat([area,gov],axis=1)
            m=model(kind,seed).fit(X.iloc[tr],y.iloc[tr]);p0=m.predict_proba(X.iloc[te]);p=np.zeros((len(te),3))
            for j,c in enumerate(m.classes_):p[:,CLASSES.index(c)]=p0[:,j]
            folds.append(dict(protocol=protocol,seed=seed,fold=fold,model=experiment,status='ok',n_train=len(tr),n_test=len(te),**metrics(y.iloc[te],p)))
            for j,i in enumerate(te):predictions.append(dict(protocol=protocol,seed=seed,fold=fold,model=experiment,row=i,group_id=g.iloc[i],y=y.iloc[i],**{f'score_{c}':p[j,k] for k,c in enumerate(CLASSES)}))
    fp=pd.DataFrame(folds);pred=pd.DataFrame(predictions)
    fp.to_csv(out/'scenario_fold_metrics.csv',index=False);pred.to_csv(out/'scenario_predictions.csv',index=False);pd.DataFrame(members).to_csv(out/'scenario_split_membership.csv',index=False)
    fp.groupby(['protocol','model'])[['macro_f1','ap_decline','ap_rise','ap_stable']].agg(['mean','std','count']).to_csv(out/'scenario_summary.csv')
    # Paired group-bootstrap conditional descriptive intervals, not a p-value.
    seed0=pred[(pred.protocol=='grouped')&pred.seed.eq(0)];original=pd.read_csv(out/'area_history_predictions.csv');original=original[(original.protocol=='grouped')&original.seed.eq(0)]
    base=original[original.model.eq('majority')].set_index('row').sort_index();groups=base.group_id.unique();rng=np.random.default_rng(20261102);intervals=[]
    for experiment in ['governance_only_logistic','governance_only_forest','combined_logistic','combined_forest']:
        kind=experiment.split('_')[-1];base=original[original.model.eq(kind)].set_index('row').sort_index()
        cand=seed0[seed0.model.eq(experiment)].set_index('row').sort_index();assert cand.index.equals(base.index)
        differences=[]
        for _ in range(1000):
            drawn=rng.choice(groups,len(groups),replace=True);indices=np.concatenate([base.index[base.group_id.eq(k)].to_numpy() for k in drawn])
            b=base.loc[indices];c=cand.loc[indices];differences.append(metrics(c.y,c[[f'score_{x}' for x in CLASSES]].to_numpy())['macro_f1']-metrics(b.y,b[[f'score_{x}' for x in CLASSES]].to_numpy())['macro_f1'])
        intervals.append(dict(model=experiment,comparison='area_only_'+kind,metric='macro_f1',point_difference=metrics(cand.y,cand[[f'score_{x}' for x in CLASSES]].to_numpy())['macro_f1']-metrics(base.y,base[[f'score_{x}' for x in CLASSES]].to_numpy())['macro_f1'],descriptive_lower=float(np.quantile(differences,.025)),descriptive_upper=float(np.quantile(differences,.975)),replicates=1000,independent_groups=len(groups),interpretation='conditional_exploratory_group_bootstrap_not_confirmatory'))
    pd.DataFrame(intervals).to_csv(out/'scenario_bootstrap.csv',index=False)
    print(fp.groupby(['protocol','model'])[['macro_f1','ap_decline']].mean().to_string());print(pd.DataFrame(intervals).to_string(index=False));print('Decline groups',table[table.outcome.eq('decline')].group_id.nunique())
if __name__=='__main__':main()

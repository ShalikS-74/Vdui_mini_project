"""Describe exclusions before selecting targets or fitting expanded models."""
from pathlib import Path
import json
import pandas as pd
import numpy as np
from pipeline import ROOT, source_file, load_source, build_table

def main():
    path, digest = source_file()
    raw = pd.read_excel(path,sheet_name='AggrSCWarAgriRelig').replace(-999,np.nan)
    filtered=load_source(path)
    counts=[]
    for name, frame in [('all_aggregate_rows',raw),('uniq_y_only',filtered)]:
        for horizon in [50,100]:
            table=build_table(frame,horizon)
            counts.append(dict(sample=name,horizon=horizon,source_rows=len(frame),observed_territory=int(frame.Terr.notna().sum()),labeled_rows=len(table),contractions=int(table.contraction.sum()),polity_groups=table.group_id.nunique(),status='descriptive_not_an_alternative_confirmatory_result'))
    out=ROOT/'data/research_audit';out.mkdir(exist_ok=True)
    pd.DataFrame(counts).to_csv(out/'sampling.csv',index=False)
    polities=pd.read_excel(path,sheet_name='Polities')
    polities.to_csv(out/'source_polity_registry.csv',index=False)
    variables=pd.read_excel(path,sheet_name='Variables')
    variables.to_csv(out/'source_variable_registry.csv',index=False)
    metadata=pd.read_excel(path,sheet_name='Metadata',header=None)
    metadata.to_csv(out/'source_sheet_notes.csv',index=False,header=False)
    raw_features=pd.read_excel(path,sheet_name='TSDat123').replace(-999,np.nan)
    raw_features.isna().mean().rename('missing_rate').to_csv(out/'raw_feature_missingness.csv')
    (out/'status.json').write_text(json.dumps({'source_sha256':digest,'interpretation':'Descriptive sampling only. Do not assume uniq=n rows are independent or change exclusion rule until source metadata is reviewed. No expanded model is fit.','next':'Source-verified mapping to Cliopatria, label and continuity audit, then pre-specified held-out experiment.'},indent=2)+'\n')
    print(pd.DataFrame(counts).to_string(index=False))
if __name__=='__main__':main()

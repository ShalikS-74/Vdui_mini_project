"""Generate a version-controlled PBIP candidate. Desktop render is required."""
from pathlib import Path
import json
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'powerbi'
if not (ROOT/'dashboard/run_metadata.json').exists():
    import sys
    sys.path.insert(0,str(ROOT/'src'))
    from bundled_exports import restore
    restore(ROOT)
def write(path,obj):
    p=OUT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,indent=2)+'\n')
def schema(part,version):return f'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/{part}/{version}/schema.json'
write('BeyondEmpire.pbip',{'version':'1.0','artifacts':[{'report':{'path':'BeyondEmpire.Report'}}],'settings':{'enableAutoRecovery':True}})
write('BeyondEmpire.Report/definition.pbir',{'version':'4.0','datasetReference':{'byPath':{'path':'../BeyondEmpire.SemanticModel'}}})
write('BeyondEmpire.SemanticModel/definition.pbism',{'version':'4.0','settings':{}})
write('BeyondEmpire.Report/definition/version.json',{'$schema':schema('versionMetadata','1.0.0'),'version':'2.0.0'})
write('BeyondEmpire.Report/definition/report.json',{'$schema':schema('report','1.3.0'),'themeCollection':{'baseTheme':{'name':'CY24SU10','reportVersionAtImport':'5.61','type':'SharedResources'}},'layoutOptimization':'None','settings':{'useEnhancedTooltips':True}})
write('BeyondEmpire.Report/definition/pages/pages.json',{'$schema':schema('pagesMetadata','1.0.0'),'pageOrder':['explorer','audit'],'activePageName':'explorer'})
for page,title in [('explorer','Historical explorer'),('audit','False-positive audit')]:
    write(f'BeyondEmpire.Report/definition/pages/{page}/page.json',{'$schema':schema('page','1.4.0'),'name':page,'displayName':title,'displayOption':'FitToPage','width':1280,'height':800})
def field(table,col,measure=False):return {('Measure' if measure else 'Column'):{'Expression':{'SourceRef':{'Entity':table}},'Property':col}}
def projection(table,col,measure=False):return {'field':field(table,col,measure),'queryRef':f'{table}.{col}'}
def visual(page,name,kind,x,y,w,h,roles=None,text=None):
    v={'visualType':kind,'drillFilterOtherVisuals':True}
    if roles:v['query']={'queryState':{role:{'projections':cols} for role,cols in roles.items()}}
    if text:v['objects']={'general':[{'properties':{'paragraphs':[{'textRuns':[{'value':text,'textStyle':{'fontSize':'15pt','fontFamily':'Segoe UI'}}]}]}}]}
    write(f'BeyondEmpire.Report/definition/pages/{page}/visuals/{name}/visual.json',{'$schema':schema('visualContainer','2.0.0'),'name':name,'position':{'x':x,'y':y,'z':0,'width':w,'height':h,'tabOrder':0},'visual':v})
caption='Beyond the Empire | Uncalibrated historical model scores. 98 rows, 6 contractions. Explanations are not causes. No modern transfer claims.'
for p in ['explorer','audit']:visual(p,'caption','textbox',20,10,1240,90,text=caption)
visual('explorer','polity','slicer',20,110,400,100,{'Values':[projection('Predictions','polity')]})
visual('explorer','year','slicer',440,110,300,100,{'Values':[projection('Predictions','time_t')]})
visual('explorer','score','card',760,110,490,100,{'Values':[projection('Predictions','Selected score',True)]})
visual('explorer','shap','barChart',20,230,780,530,{'Category':[projection('Explanations','feature')],'Y':[projection('Explanations','SHAP contribution',True)]})
visual('explorer','observed','tableEx',820,230,430,530,{'Values':[projection('Predictions',x) for x in ['polity','time_t','outcome','model_score']]})
visual('audit','reviewnote','textbox',20,110,1240,70,text='Fixed OOF score >= 0.70; no observed contraction. All historical verdicts pending sourced manual review. Non-contraction is not proof of genuine survival.')
visual('audit','cases','tableEx',20,200,1240,550,{'Values':[projection('Cases',x) for x in ['polity','century','oof_p_decline','true_label','type','note']]})
model=OUT/'BeyondEmpire.SemanticModel/definition';model.mkdir(parents=True,exist_ok=True)
(model/'database.tmdl').write_text('database\n\tcompatibilityLevel: 1601\n')
(model/'model.tmdl').write_text('model Model\n\tculture: en-US\n\tdefaultPowerBIDataSourceVersion: powerBI_V3\n\tsourceQueryCulture: en-US\n\nref table Predictions\nref table Explanations\nref table Cases\n\nref expression DataRoot\n')
(model/'expressions.tmdl').write_text('expression DataRoot = "C:\\CHANGE_ME\\Vdui_mini_project\\dashboard" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]\n')
(model/'relationships.tmdl').write_text('relationship explanation_to_observation\n\tfromColumn: Explanations.observation_id\n\ttoColumn: Predictions.observation_id\n\nrelationship case_to_observation\n\tfromColumn: Cases.observation_id\n\ttoColumn: Predictions.observation_id\n')
for table,file in [('Predictions','predictions.csv'),('Explanations','shap_long.csv'),('Cases','fp_cases.csv')]:
    df=pd.read_csv(ROOT/'dashboard'/file)
    year='century' if table=='Cases' else 'time_t'
    measures=''
    if table=='Predictions':measures="\tmeasure 'Selected score' = SELECTEDVALUE(Predictions[model_score])\n\t\tformatString: 0.000\n\n"
    if table=='Explanations':measures="\tmeasure 'SHAP contribution' = SUM(Explanations[shap_value])\n\t\tformatString: 0.000\n\n"
    text=f'table {table}\n\n'+measures
    for col in list(df)+['observation_id']:
        dtype='string' if col=='observation_id' or not pd.api.types.is_numeric_dtype(df[col]) else ('int64' if pd.api.types.is_integer_dtype(df[col]) else 'double')
        text+=f'\tcolumn {col}\n\t\tdataType: {dtype}\n\t\tsummarizeBy: none\n\t\tsourceColumn: {col}\n\n'
    conversions=', '.join('{"'+c+'", '+('Int64.Type' if pd.api.types.is_integer_dtype(df[c]) else 'type number' if pd.api.types.is_numeric_dtype(df[c]) else 'type text')+'}' for c in df)
    text+=f'''\tpartition {table} = m
\t\tmode: import
\t\tsource =
\t\t\tlet
\t\t\t    Source = Csv.Document(File.Contents(DataRoot & "\\{file}"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
\t\t\t    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t    Typed = Table.TransformColumnTypes(Headers, {{{conversions}}}),
\t\t\t    Keyed = Table.AddColumn(Typed, "observation_id", each [polity] & "|" & Text.From([{year}]), type text)
\t\t\tin
\t\t\t    Keyed
'''
    p=model/'tables'/f'{table}.tmdl';p.parent.mkdir(exist_ok=True);p.write_text(text)
print('Generated PBIP candidate. Requires Power BI Desktop open, refresh and visual verification.')

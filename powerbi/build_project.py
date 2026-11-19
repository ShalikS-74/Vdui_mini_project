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
write('BeyondEmpire.SemanticModel/definition.pbism',{'version':'4.2','settings':{}})
write('BeyondEmpire.Report/definition/version.json',{'$schema':schema('versionMetadata','1.0.0'),'version':'2.0.0'})
write('BeyondEmpire.Report/definition/report.json',{'$schema':schema('report','1.3.0'),'themeCollection':{'baseTheme':{'name':'CY24SU10','reportVersionAtImport':'5.61','type':'SharedResources'}},'layoutOptimization':'None','settings':{'useEnhancedTooltips':True}})
write('BeyondEmpire.Report/definition/pages/pages.json',{'$schema':schema('pagesMetadata','1.1.0'),'pageOrder':['explorer','audit'],'activePageName':'explorer'})
for page,title in [('explorer','Historical explorer'),('audit','False-positive audit')]:
    pj={'$schema':schema('page','1.4.0'),'name':page,'displayName':title,'displayOption':'FitToPage','width':1280,'height':800}
    if page=='audit':pj['visualInteractions']=[{'source':a,'target':b,'type':'NoFilter'} for a,bs in (('cases',('queuecount','scatter')),('scatter',('queuecount','cases'))) for b in bs]
    write(f'BeyondEmpire.Report/definition/pages/{page}/page.json',pj)
def field(table,col,measure=False):return {('Measure' if measure else 'Column'):{'Expression':{'SourceRef':{'Entity':table}},'Property':col}}
def projection(table,col,measure=False):return {'field':field(table,col,measure),'queryRef':f'{table}.{col}'}
def visual(page,name,kind,x,y,w,h,roles=None,text=None,title=None,tab=0,font_size='11pt',font_weight=None,objects=None,filter_config=None):
    v={'visualType':kind,'drillFilterOtherVisuals':True}
    if roles:v['query']={'queryState':{role:{'projections':cols} for role,cols in roles.items()}}
    if text:
        text_style={'fontSize':font_size,'fontFamily':'Segoe UI'}
        if font_weight:text_style['fontWeight']=font_weight
        v['objects']={'general':[{'properties':{'paragraphs':[{'textRuns':[{'value':text,'textStyle':text_style}]}]}}]}
    container={}
    if title:container['title']=[{'properties':{'show':{'expr':{'Literal':{'Value':'true'}}},'text':{'expr':{'Literal':{'Value':repr(title)}}}}}]
    if container:v['visualContainerObjects']=container
    if objects:
        v['objects']=objects
    if filter_config:
        pass
    out={'$schema':schema('visualContainer','2.14.0'),'name':name,'position':{'x':x,'y':y,'z':0,'width':w,'height':h,'tabOrder':tab},'visual':v}
    if filter_config:
        out['filterConfig']=filter_config
    write(f'BeyondEmpire.Report/definition/pages/{page}/visuals/{name}/visual.json',out)
visual('explorer','caption','textbox',32,24,1216,42,text='BEYOND THE EMPIRE  /  HISTORICAL EXPLORER',font_size='22pt',font_weight='bold',tab=0)
visual('explorer','context','textbox',32,72,1216,38,text='Inspect one held-out observation at a time. Scores rank model outputs; they are not probabilities or historical causes.',font_size='11pt',tab=1)
visual('explorer','polity','slicer',32,132,320,150,{'Values':[projection('Predictions','polity')]},title='1  Select a polity',tab=2)
visual('explorer','year','slicer',368,132,260,150,{'Values':[projection('Predictions','time_t')]},title='2  Select an observed year',tab=3)
visual('explorer','score','card',644,132,604,150,{'Values':[projection('Predictions','Selected score',True)]},title='Selected held-out score  •  uncalibrated',tab=4)
visual('explorer','shap','barChart',32,316,720,444,{'Category':[projection('Explanations','feature')],'Y':[projection('Explanations','SHAP contribution',True)]},title='Why the model gave this score  •  SHAP contribution (log-odds)',tab=5)
visual('explorer','observed','tableEx',776,316,472,444,{'Values':[projection('Predictions',x) for x in ['polity','time_t','outcome','model_score']]},title='Held-out observations  •  filtered by selection',tab=6)
visual('audit','caption','textbox',32,20,1216,48,text='BEYOND THE EMPIRE  /  FALSE-POSITIVE AUDIT',font_size='22pt',font_weight='bold',tab=0)
threshold_objects={'data':[{'properties':{'mode':{'expr':{'Literal':{'Value':"'Dropdown'"}}}}}]}
visual('audit','threshold','slicer',32,84,300,96,{'Values':[projection('Threshold','Threshold')]},title='Audit threshold',tab=1,objects=threshold_objects)
visual('audit','queuecount','card',348,84,284,96,{'Values':[projection('Cases','Flagged cases',True)]},title='Flagged cases',tab=2)
case_filter={'filters':[{
    'name':'audit_threshold_filter',
    'field':{'Measure':{'Expression':{'SourceRef':{'Entity':'Cases'}},'Property':'Audit case match'}},
    'type':'Advanced',
    'filter':{
        'Version':2,
        'From':[{'Name':'C','Entity':'Cases','Type':0}],
        'Where':[{'Condition':{'Comparison':{
            'ComparisonKind':0,
            'Left':{'Measure':{'Expression':{'SourceRef':{'Source':'C'}},'Property':'Audit case match'}},
            'Right':{'Literal':{'Value':'1L'}}
        }}}]
    }
}]}
visual('audit','cases','tableEx',32,196,600,544,{'Values':[projection('Cases',x) for x in ['polity','century','oof_p_decline','true_label']]},title='Cases at or above the threshold',tab=3,filter_config=case_filter)
visual('audit','scatter','scatterChart',648,196,600,544,{'Details':[projection('Predictions','observation_id')],'X':[projection('Predictions','time_t')],'Y':[projection('Predictions','Threshold scatter score',True)]},title='Score by observed year  (flagged cases at the selected threshold)',tab=4)
model=OUT/'BeyondEmpire.SemanticModel/definition';model.mkdir(parents=True,exist_ok=True)
(model/'database.tmdl').write_text('database\n\tcompatibilityLevel: 1601\n')
(model/'model.tmdl').write_text('model Model\n\tculture: en-US\n\tdefaultPowerBIDataSourceVersion: powerBI_V3\n\tsourceQueryCulture: en-US\n\nref table Threshold\nref table Predictions\nref table Explanations\nref table Cases\n\nref expression DataRoot\n')
(model/'expressions.tmdl').write_text('expression DataRoot = "C:\\Users\\Spoorthi AN\\Vdui_mini_project\\dashboard" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]\n')
(model/'relationships.tmdl').write_text('relationship explanation_to_observation\n\tfromColumn: Explanations.observation_id\n\ttoColumn: Predictions.observation_id\n\nrelationship case_to_observation\n\tfromColumn: Cases.observation_id\n\ttoColumn: Predictions.observation_id\n')
for table,file in [('Predictions','predictions.csv'),('Explanations','shap_long.csv'),('Cases','fp_cases.csv')]:
    df=pd.read_csv(ROOT/'dashboard'/file)
    year='century' if table=='Cases' else 'time_t'
    measures=''
    if table=='Predictions':measures="""\tmeasure 'Selected score' = SELECTEDVALUE(Predictions[model_score])
\t\tformatString: 0.000

\tmeasure 'Mean model score' = AVERAGE(Predictions[model_score])
\t\tformatString: 0.000

\tmeasure 'Threshold scatter score' =
\t\t\tVAR T = IF(ISFILTERED(Threshold[Threshold]), MIN(Threshold[Threshold]), 0.70)
\t\t\tVAR S = CALCULATE(MAX(Cases[oof_p_decline]))
\t\t\tRETURN IF(NOT(ISBLANK(S)) && S >= T, SELECTEDVALUE(Predictions[model_score]), BLANK())
\t\tformatString: 0.000

"""
    if table=='Explanations':measures="\tmeasure 'SHAP contribution' = SUM(Explanations[shap_value])\n\t\tformatString: 0.000\n\n"
    if table=='Cases':measures="\tmeasure 'Audit case match' =\n\t\t\tVAR T = IF(ISFILTERED(Threshold[Threshold]), MIN(Threshold[Threshold]), 0.70)\n\t\t\tRETURN IF(MAX(Cases[oof_p_decline]) >= T, 1, 0)\n\t\tformatString: 0\n\n\tmeasure 'Flagged cases' =\n\t\t\tVAR T = IF(ISFILTERED(Threshold[Threshold]), MIN(Threshold[Threshold]), 0.70)\n\t\t\tRETURN CALCULATE(COUNTROWS(Cases), Cases[oof_p_decline] >= T)\n\t\tformatString: 0\n\n"
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
(model/'tables'/ 'Threshold.tmdl').write_text('table Threshold\n\n\tmeasure \'Threshold value\' = IF(ISFILTERED(Threshold[Threshold]), MIN(Threshold[Threshold]), 0.70)\n\t\tformatString: 0%\n\n\tcolumn Threshold\n\t\tdataType: double\n\t\tsummarizeBy: none\n\t\tsourceColumn: Threshold\n\n\tpartition Threshold = m\n\t\tmode: import\n\t\tsource =\n\t\t\tlet\n\t\t\t    Source = #table({"Threshold"}, {{0.3}, {0.5}, {0.7}, {0.9}}),\n\t\t\t    Typed = Table.TransformColumnTypes(Source, {{"Threshold", type number}})\n\t\t\tin\n\t\t\t    Typed\n')
print('Generated PBIP candidate. Requires Power BI Desktop open, refresh and visual verification.')

"""Generate a version-controlled PBIP candidate. Desktop render is required."""
from pathlib import Path
import json
import shutil
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
write('BeyondEmpire.Report/definition/pages/pages.json',{'$schema':schema('pagesMetadata','1.1.0'),'pageOrder':['explorer','audit','thresholds'],'activePageName':'explorer'})
for page,title in [('explorer','Historical explorer'),('audit','False-positive audit'),('thresholds','Threshold results')]:
    write(f'BeyondEmpire.Report/definition/pages/{page}/page.json',{'$schema':schema('page','1.4.0'),'name':page,'displayName':title,'displayOption':'FitToPage','width':1280,'height':800})
def field(table,col,measure=False):return {('Measure' if measure else 'Column'):{'Expression':{'SourceRef':{'Entity':table}},'Property':col}}
def projection(table,col,measure=False,display=None):
    p={'field':field(table,col,measure),'queryRef':f'{table}.{col}'}
    if display:p['displayName']=display
    return p
def reset_visuals(page):
    d=OUT/f'BeyondEmpire.Report/definition/pages/{page}/visuals'
    if d.exists():shutil.rmtree(d)
def visual(page,name,kind,x,y,w,h,roles=None,text=None,title=None,tab=0,font_size='11pt',font_weight=None,objects=None,filter_config=None,sort_definition=None):
    v={'visualType':kind,'drillFilterOtherVisuals':True}
    if roles:
        v['query']={'queryState':{role:{'projections':cols} for role,cols in roles.items()}}
        if sort_definition:v['query']['sortDefinition']=sort_definition
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
reset_visuals('explorer')
visual('explorer','caption','textbox',32,24,1216,42,text='BEYOND THE EMPIRE  /  HISTORICAL EXPLORER',font_size='22pt',font_weight='bold',tab=0)
visual('explorer','context','textbox',32,72,1216,38,text='Inspect one held-out observation at a time. Scores rank model outputs; they are not probabilities or historical causes.',font_size='11pt',tab=1)
visual('explorer','polity','slicer',32,132,320,150,{'Values':[projection('Predictions','polity')]},title='1  Select a polity',tab=2)
visual('explorer','year','slicer',368,132,260,150,{'Values':[projection('Predictions','time_t')]},title='2  Select an observed year',tab=3)
visual('explorer','score','card',644,132,604,150,{'Values':[projection('Predictions','Selected score',True)]},title='Selected held-out score  •  uncalibrated',tab=4)
visual('explorer','shap','barChart',32,316,720,444,{'Category':[projection('Explanations','feature')],'Y':[projection('Explanations','SHAP contribution',True)]},title='Why the model gave this score  •  SHAP contribution (log-odds)',tab=5)
visual('explorer','observed','tableEx',776,316,472,444,{'Values':[projection('Predictions',x) for x in ['polity','time_t','outcome','model_score']]},title='Held-out observations  •  filtered by selection',tab=6)
reset_visuals('audit')
visual('audit','caption','textbox',32,24,1216,42,text='BEYOND THE EMPIRE  /  FALSE-POSITIVE AUDIT',font_size='22pt',font_weight='bold',tab=0)
visual('audit','context','textbox',32,72,1216,38,text='Pick an audit threshold from the dropdown. The cards, queue table and scatter all update together to show the review queue at that cutoff.',font_size='11pt',tab=1)
threshold_objects={'data':[{'properties':{'mode':{'expr':{'Literal':{'Value':"'Dropdown'"}}}}}],'selection':[{'properties':{'singleSelect':{'expr':{'Literal':{'Value':'true'}}}}}]}
visual('audit','threshold','slicer',32,132,220,82,{'Values':[projection('Threshold','Threshold')]},title='Audit threshold',tab=2,objects=threshold_objects)
visual('audit','selected','card',268,132,200,82,{'Values':[projection('Threshold','Threshold value',True)]},title='Selected threshold',tab=3)
visual('audit','queuecount','card',484,132,200,82,{'Values':[projection('Predictions','Audit queue rows',True)]},title='Rows in current queue',tab=4)
visual('audit','reviewset','card',700,132,220,82,{'Values':[projection('Cases','Case-set rows in queue',True)]},title='Of which in the original 0.70 case set',tab=5)
visual('audit','reviewnote','textbox',936,132,312,82,text='AUDIT RULE  •  Score at or above the selected threshold and no observed contraction. Flagged case-set rows remain pending sourced historical review.',font_size='11pt',font_weight='bold',tab=6)
queue_filter={'filters':[{
    'name':'audit_queue_filter',
    'field':{'Measure':{'Expression':{'SourceRef':{'Entity':'Predictions'}},'Property':'In audit queue'}},
    'type':'Advanced',
    'filter':{
        'Version':2,
        'From':[{'Name':'P','Entity':'Predictions','Type':0}],
        'Where':[{'Condition':{'Comparison':{
            'ComparisonKind':0,
            'Left':{'Measure':{'Expression':{'SourceRef':{'Source':'P'}},'Property':'In audit queue'}},
            'Right':{'Literal':{'Value':'1L'}}
        }}}]
    }
}]}
visual('audit','queue','tableEx',32,226,1216,280,{'Values':[
    projection('Predictions','polity',display='Polity'),
    projection('Predictions','time_t',display='Observed year'),
    projection('Predictions','Row score',True,display='Model score'),
    projection('Predictions','outcome',display='Observed outcome (area proxy)'),
    projection('Predictions','In original 0.70 case set',True),
    projection('Predictions','Case note (pending review)',True)]},title='Audit queue at the selected threshold  •  high score, no observed contraction, highest scores first',tab=7,filter_config=queue_filter,sort_definition={'sort':[{'field':field('Predictions','Row score',True),'direction':'Descending'}],'isDefaultSort':True})
visual('audit','scatter','scatterChart',32,522,1216,238,{'Details':[projection('Predictions','observation_id')],'X':[projection('Predictions','time_t')],'Y':[projection('Predictions','Threshold scatter score',True)]},title='Score by observed year  •  only queue rows at the selected threshold are plotted',tab=8)
reset_visuals('thresholds')
visual('thresholds','caption','textbox',32,24,1216,42,text='BEYOND THE EMPIRE  /  THRESHOLD RESULTS',font_size='22pt',font_weight='bold',tab=0)
visual('thresholds','context','textbox',32,72,1216,38,text='One trained model is scored once per held-out row; each audit threshold only re-classifies the same scores. No per-threshold retraining. Exploratory: six observed declines.',font_size='11pt',tab=1)
visual('thresholds','model','slicer',32,132,220,120,{'Values':[projection('ThresholdResults','model')]},title='Model',tab=2)
visual('thresholds','protocol','slicer',268,132,220,120,{'Values':[projection('ThresholdResults','protocol')]},title='Evaluation protocol',tab=3)
visual('thresholds','means','tableEx',504,132,744,120,{'Values':[projection('ThresholdResults','Mean audit queue',True),projection('ThresholdResults','Mean recall',True),projection('ThresholdResults','Mean precision',True),projection('ThresholdResults','Mean F1',True)]},title='Means across seeds at the selected filters',tab=4)
visual('thresholds','results','tableEx',32,268,1216,240,{'Values':[projection('ThresholdResults',x) for x in ['protocol','model','seed','threshold','n','tp','fp','fn','tn','precision','recall','f1','audit_queue']]},title='Held-out results by threshold  •  per evaluation seed',tab=5)
visual('thresholds','queuechart','clusteredColumnChart',32,532,600,228,{'Category':[projection('ThresholdResults','threshold')],'Y':[projection('ThresholdResults','Mean audit queue',True)]},title='False-alarm queue size by threshold  •  mean across seeds',tab=6)
visual('thresholds','prchart','lineChart',648,532,600,228,{'Category':[projection('ThresholdResults','threshold')],'Y':[projection('ThresholdResults','Mean recall',True),projection('ThresholdResults','Mean precision',True)]},title='Recall and precision by threshold  •  mean across seeds',tab=7)
model=OUT/'BeyondEmpire.SemanticModel/definition';model.mkdir(parents=True,exist_ok=True)
(model/'database.tmdl').write_text('database\n\tcompatibilityLevel: 1601\n')
(model/'model.tmdl').write_text('model Model\n\tculture: en-US\n\tdefaultPowerBIDataSourceVersion: powerBI_V3\n\tsourceQueryCulture: en-US\n\nref table Predictions\nref table Explanations\nref table Cases\nref table Threshold\nref table ThresholdResults\n\nref expression DataRoot\n')
existing=model/'expressions.tmdl'
if existing.exists() and 'CHANGE_ME' not in existing.read_text():
    data_root=existing.read_text()
else:
    data_root='expression DataRoot = "C:\\CHANGE_ME\\Vdui_mini_project\\dashboard" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]\n'
(model/'expressions.tmdl').write_text(data_root)
(model/'relationships.tmdl').write_text('relationship explanation_to_observation\n\tfromColumn: Explanations.observation_id\n\ttoColumn: Predictions.observation_id\n\nrelationship case_to_observation\n\tfromColumn: Cases.observation_id\n\ttoColumn: Predictions.observation_id\n')
for table,file in [('Predictions','predictions.csv'),('Explanations','shap_long.csv'),('Cases','fp_cases.csv')]:
    df=pd.read_csv(ROOT/'dashboard'/file)
    year='century' if table=='Cases' else 'time_t'
    measures=''
    if table=='Predictions':measures="""\tmeasure 'Selected score' = SELECTEDVALUE(Predictions[model_score])
\t\tformatString: 0.000

\tmeasure 'Mean model score' = AVERAGE(Predictions[model_score])
\t\tformatString: 0.000

\tmeasure 'Audit queue rows' = COUNTROWS(FILTER(Predictions, Predictions[model_score] >= [Threshold value] && Predictions[contraction] = 0))
\t\tformatString: 0

\tmeasure 'Threshold scatter score' =
\t\tVAR RowScore = SELECTEDVALUE(Predictions[model_score])
\t\tVAR RowOutcome = SELECTEDVALUE(Predictions[contraction])
\t\tRETURN IF(NOT(ISBLANK(RowScore)) && RowOutcome = 0 && RowScore >= [Threshold value], RowScore, BLANK())
\t\tformatString: 0.000

\tmeasure 'In audit queue' = IF(MAX(Predictions[model_score]) >= [Threshold value] && MAX(Predictions[contraction]) = 0, 1, 0)
\t\tformatString: 0

\tmeasure 'Row score' = MAX(Predictions[model_score])
\t\tformatString: 0.000

\tmeasure 'In original 0.70 case set' = IF(COALESCE(COUNTROWS(Cases), 0) > 0, "yes", "no")

\tmeasure 'Case note (pending review)' = MAX(Cases[note])

"""
    if table=='Explanations':measures="\tmeasure 'SHAP contribution' = SUM(Explanations[shap_value])\n\t\tformatString: 0.000\n\n"
    if table=='Cases':measures="\tmeasure 'Audit case match' = IF(MAX(Cases[oof_p_decline]) >= [Threshold value], 1, 0)\n\t\tformatString: 0\n\n\tmeasure 'Case-set rows in queue' = COUNTROWS(FILTER(Cases, Cases[oof_p_decline] >= [Threshold value]))\n\t\tformatString: 0\n\n"
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
(model/'tables'/ 'Threshold.tmdl').write_text('''table Threshold
    measure 'Threshold value' = SELECTEDVALUE(Threshold[Threshold], 0.70)
        formatString: 0%

    column Threshold
        dataType: double
        summarizeBy: none
        sourceColumn: Threshold

    partition Threshold = m
        mode: import
        source =
            let
                Source = #table(
                    {"Threshold"},
                    {
                        {0.50}, {0.60}, {0.70}, {0.80}
                    }
                )
            in
                Source
''')
tdf=pd.read_csv(ROOT/'dashboard'/'threshold_results.csv')
ttext='''table ThresholdResults

\tmeasure 'Mean audit queue' = AVERAGE(ThresholdResults[audit_queue])
\t\tformatString: 0.0

\tmeasure 'Mean recall' = AVERAGE(ThresholdResults[recall])
\t\tformatString: 0.000

\tmeasure 'Mean precision' = AVERAGE(ThresholdResults[precision])
\t\tformatString: 0.000

\tmeasure 'Mean F1' = AVERAGE(ThresholdResults[f1])
\t\tformatString: 0.000

'''
for col in tdf:
    dtype='string' if not pd.api.types.is_numeric_dtype(tdf[col]) else ('int64' if pd.api.types.is_integer_dtype(tdf[col]) else 'double')
    ttext+=f'\tcolumn {col}\n\t\tdataType: {dtype}\n\t\tsummarizeBy: none\n\t\tsourceColumn: {col}\n\n'
tconv=', '.join('{"'+c+'", '+('Int64.Type' if pd.api.types.is_integer_dtype(tdf[c]) else 'type number' if pd.api.types.is_numeric_dtype(tdf[c]) else 'type text')+'}' for c in tdf)
ttext+=f'''\tpartition ThresholdResults = m
\t\tmode: import
\t\tsource =
\t\t\tlet
\t\t\t    Source = Csv.Document(File.Contents(DataRoot & "\\threshold_results.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
\t\t\t    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t    Typed = Table.TransformColumnTypes(Headers, {{{tconv}}})
\t\t\tin
\t\t\t    Typed
'''
(model/'tables'/'ThresholdResults.tmdl').write_text(ttext)
print('Generated PBIP candidate. Requires Power BI Desktop open, refresh and visual verification.')

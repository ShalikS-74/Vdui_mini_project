"""Offline checks for the PBIP candidate: field references, page wiring and
audit-page threshold behaviour. Rendering still requires Power BI Desktop."""
import json
import re
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'app.py').exists())
DEF = ROOT / 'powerbi' / 'BeyondEmpire.Report' / 'definition'
MODEL = ROOT / 'powerbi' / 'BeyondEmpire.SemanticModel' / 'definition'


def model_fields():
    tables = {}
    for f in (MODEL / 'tables').glob('*.tmdl'):
        text = f.read_text()
        name = re.match(r'table\s+(\w+)', text).group(1)
        tables[name] = {
            'Column': set(re.findall(r'^\s*column\s+([A-Za-z_]\w*)', text, re.M)),
            'Measure': set(re.findall(r"^\s*measure\s+'([^']+)'", text, re.M)),
        }
    return tables


def refs(obj, path=''):
    if isinstance(obj, dict):
        for kind in ('Column', 'Measure'):
            node = obj.get(kind)
            if isinstance(node, dict) and 'Expression' in node:
                yield kind, node, path
        for key, value in obj.items():
            yield from refs(value, f'{path}.{key}')
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            yield from refs(value, f'{path}[{i}]')


def visual_docs():
    for vf in sorted(DEF.glob('pages/*/visuals/*/visual.json')):
        yield vf, json.loads(vf.read_text())


def test_visual_field_references_resolve():
    tables = model_fields()
    docs = list(visual_docs())
    assert docs, 'no visuals found'
    for vf, doc in docs:
        for kind, node, path in refs(doc):
            src = node['Expression'].get('SourceRef', {})
            if 'Entity' not in src:
                continue  # filter aliases checked separately
            assert src['Entity'] in tables, f'{vf} {path}: unknown table {src["Entity"]}'
            assert node['Property'] in tables[src['Entity']][kind], (
                f'{vf} {path}: {src["Entity"]}.{node["Property"]} is not a {kind}')


def test_filter_aliases_declared():
    for vf, doc in visual_docs():
        for flt in doc.get('filterConfig', {}).get('filters', []):
            declared = {e['Name'] for e in flt['filter']['From']}
            for kind, node, path in refs(flt):
                src = node['Expression'].get('SourceRef', {})
                if 'Source' in src:
                    assert src['Source'] in declared, f'{vf}: undeclared alias {src["Source"]}'


def test_pages_wiring():
    meta = json.loads((DEF / 'pages' / 'pages.json').read_text())
    for page in meta['pageOrder']:
        assert (DEF / 'pages' / page / 'page.json').exists(), page
    assert meta['activePageName'] in meta['pageOrder']


def test_threshold_values_fixed_set():
    text = (MODEL / 'tables' / 'Threshold.tmdl').read_text()
    assert re.findall(r'\{(0\.\d+)\}', text) == ['0.50', '0.60', '0.70', '0.80']


def test_audit_threshold_dropdown_drives_queue():
    tables = model_fields()
    slicer = json.loads((DEF / 'pages' / 'audit' / 'visuals' / 'threshold' / 'visual.json').read_text())
    modes = [o['properties']['mode']['expr']['Literal']['Value'] for o in slicer['visual']['objects']['data']]
    assert modes == ["'Dropdown'"]
    single = slicer['visual']['objects']['selection'][0]['properties']['singleSelect']['expr']['Literal']['Value']
    assert single == 'true'
    assert 'In audit queue' in tables['Predictions']['Measure']
    assert 'In original 0.70 case set' in tables['Predictions']['Measure']
    assert 'Case note (pending review)' in tables['Predictions']['Measure']
    assert 'Case-set rows in queue' in tables['Cases']['Measure']
    queue = json.loads((DEF / 'pages' / 'audit' / 'visuals' / 'queue' / 'visual.json').read_text())
    used = {node['Property'] for _, node, _ in refs(queue)
            if node['Expression'].get('SourceRef', {}).get('Entity') == 'Predictions'}
    assert 'In audit queue' in used
    projections = queue['visual']['query']['queryState']['Values']['projections']
    outcome = next(p for p in projections if p['queryRef'] == 'Predictions.outcome')
    assert outcome['displayName'] == 'Observed outcome (area proxy)'
    sort = queue['visual']['query']['sortDefinition']['sort'][0]
    assert sort['direction'] == 'Descending'


def test_audit_queue_matches_predictions_csv():
    import pandas as pd
    pred = pd.read_csv(ROOT / 'dashboard' / 'predictions.csv')
    counts = [int(((pred.model_score >= t) & (pred.contraction == 0)).sum())
              for t in (.5, .6, .7, .8)]
    assert counts == [30, 19, 14, 11]
    cases = pd.read_csv(ROOT / 'dashboard' / 'fp_cases.csv')
    queue_at_70 = pred[(pred.model_score >= .7) & (pred.contraction == 0)]
    assert (set(queue_at_70.polity + '|' + queue_at_70.time_t.astype(str))
            == set(cases.polity + '|' + cases.century.astype(str)))

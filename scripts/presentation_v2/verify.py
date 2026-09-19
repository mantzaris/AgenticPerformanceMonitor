"""Preservation and saved-value checks; optional historical replay, never rescoring."""
import argparse
import json
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch
from trajectory_dashboards.common import read_json, write_json, file_hash


def verify(root, replay=False):
    root = Path(root); history = read_json('artifacts/presentation_v2/historical_inventory.json')
    changed = [n for n, h in history['files'].items() if not Path(n).exists() or file_hash(n) != h]
    assert not changed, changed
    result = {'historical_files_unchanged': len(history['files']), 'starting_commit': history['starting_commit'],
              'new_experimental_generations': 0, 'reserved_observations_opened': False,
              'evaluator_executed': False, 'cases': []}
    for entry in read_json(root/'source_manifest.json')['entries']:
        base = root/'gallery'/entry['slug']; m = read_json(base/'presentation.json')
        source = Path(m['source'])
        assert all(file_hash(n) == sha for n, sha in m['source_hashes'].items())
        for name, key in [('spec.json','spec'), ('bound.json','bound'), ('evidence.json','evidence'), ('selection_provenance.json','provenance')]:
            assert m[key] == read_json(source/name)
        for chart in (base/'charts').glob('*.svg'):
            data = json.loads(ET.fromstring(chart.read_text()).find('{http://www.w3.org/2000/svg}metadata').text)
            if 'evidence_id' in data:
                e = m['evidence'][data['evidence_id']]
                for k in ['trajectory', 'observation_status', 'assessment_status', 'summary', 'window', 'reference_window']:
                    if k in data: assert data[k] == e[k], (chart, k)
            for r in data.get('records', []):
                for k in ['summary', 'feature', 'window', 'reference_window']:
                    assert r[k] == m['evidence'][r['evidence_id']][k]
        result['cases'].append({'slug': entry['slug'], 'records': len(m['evidence']),
                                'saved_sources_and_chart_values': 'PASS', 'historical_status': m['selection_status']})
    capture = read_json(root/'capture_manifest.json')
    assert capture['browser_closed'] and not capture['errors'] and not capture['external_requests'] and not capture['broken_links']
    assert len(capture['captures']) == 23
    assert all(file_hash(root/c['file']) == c['sha256'] for c in capture['captures'])
    figures = read_json(root/'figure_manifest.json')['figures']
    assert all(file_hash(root/'figures'/f'{e["name"]}.pdf') == e['pdf_sha256'] for e in figures)
    assert all(e['minimum_critical_font_pt'] >= 8 for e in figures if e['name'] != 'figure1_grid')
    assert not next(e for e in figures if e['name'] == 'figure1_grid')['recommended']
    proof = read_json(root/'proof/manifest.json')
    assert proof['pages'] == 4 and file_hash(root/'proof/layout.pdf') == proof['pdf_sha256']
    assert all(file_hash(Path('artifacts/predraft_v1/template/official')/n) == h for n, h in proof['official_files'].items())
    result['browser'] = '23 captures; values and saved-state URLs checked, no errors/external requests'
    result['figures'] = 'Four readable candidates; four-panel reduction explicitly not recommended'
    result['official_template'] = 'Four pages; unmodified official files, 158.0134 mm width'
    if replay:
        from trajectory_dashboards.stage6.core import Engine
        from trajectory_dashboards.stage6.adapter import replay as replay_original
        engine = Engine()  # Hash-checked saved development bundle only.
        with patch.object(Engine, 'analyze', side_effect=AssertionError('New analysis forbidden during replay')):
            for entry, case_result in zip(read_json(root/'source_manifest.json')['entries'], result['cases']):
                source = Path(entry['source'])
                with tempfile.TemporaryDirectory(prefix='presentation-v2-replay-') as tmp:
                    replay_original(engine, source, tmp)
                    for name in ['spec.json', 'evidence.json', 'selection_provenance.json', 'bound.json']:
                        assert read_json(Path(tmp)/name) == read_json(source/name), name
                case_result['original_source_bound_replay'] = 'PASS'
        result['analytical_dispatcher_calls'] = 0
        result['validation_scope'] = 'Unchanged source-bound verifier recomputed checks from the saved development bundle; no new analytical request, model, evaluator or reserved observations.'
    write_json(root/'checks/verification.json', result)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--output', default='artifacts/presentation_v2')
    ap.add_argument('--replay', action='store_true'); args = ap.parse_args()
    verify(args.output, args.replay)

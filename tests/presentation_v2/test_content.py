"""Changed presentation boundaries; no scoring or new analytical calculations."""
from copy import deepcopy
import json
from pathlib import Path
import pytest
from trajectory_dashboards.presentation_v1.model import load, EXAMPLES
from trajectory_dashboards.presentation_v2.render import render

@pytest.mark.parametrize('slug,label,condition,case', EXAMPLES)
def test_complete_saved_content_and_provenance_survive(slug, label, condition, case, tmp_path):
    m = load(f'artifacts/stage6/comparison/{condition}/{case}/accepted', label)
    before = deepcopy(m); render(m, tmp_path)
    assert m == before
    exported = json.loads((tmp_path/'presentation.json').read_text())
    assert exported['evidence'] == before['evidence']
    assert exported['spec'] == before['spec'] and exported['provenance'] == before['provenance']
    v2 = json.loads((tmp_path/'presentation_v2.json').read_text())
    assert sorted(i for c in v2['selected_answer_evidence'] for i in c['original_indices']) == list(range(len(m['spec']['claims'])))
    assert v2['original_panels'] == m['panels']
    assert not v2['new_substantive_answers'] and not v2['answer_completeness_evaluated']

def test_failure_keeps_personal_insufficiency_and_only_earlier_peer_answers(tmp_path):
    m = load('artifacts/stage6/comparison/compact_a/s6_15/accepted', 'Anonymous')
    render(m, tmp_path)
    for route in ['index.html', 'figure.html']:
        page = (tmp_path/route).read_text()
        assert 'Personal comparison unavailable' in page
        assert 'Peer comparison unavailable' not in page
        for eid, e in m['evidence'].items():
            if e['window'] == [10, 11]:
                assert f'data-answer="peer" data-evidence="{eid}"' not in page
    assert len(m['comparison_ids']) == 2

def test_layout_is_semantic_and_historical_repair_is_not_a_new_repair(tmp_path):
    m = load('artifacts/stage6/comparison/compact_a/s6_09/accepted', 'Anonymous')
    m['question']['question_id'] = 'not-the-original-id'
    m['question']['kind'] = 'no-layout-instruction'
    render(m, tmp_path)
    content = (tmp_path/'figure.html').read_text()
    assert 'data-layout="observations"' in content and 'historically repaired' in content
    assert 'Original compiler: observation timeline' in content
    assert 'Unavailable' in content and 'Unavailable is not zero' in content

def test_controls_expose_only_claim_selected_compatible_references(tmp_path):
    m = load('artifacts/stage6/comparison/compact_a/s6_05/accepted', 'Anonymous')
    render(m, tmp_path)
    for route in ['index.html', 'figure.html']:
        html = (tmp_path/route).read_text()
        payload = html.split('<script id="saved-state" type="application/json">')[1].split('</script>')[0]
        states = json.loads(payload)['references']
        assert set(states) == set(m['comparison_ids'])
        assert all(states[k]['summary'] == m['evidence'][k]['summary'] for k in states)
        assert all(states[k]['window'] == [8, 11] for k in states)
        assert len({states[k]['summary']['focal_mean'] for k in states}) == 1

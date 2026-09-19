"""Scientific presentation boundaries, not CSS snapshots or a new evaluator."""
from copy import deepcopy
import json
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET
import pytest
from trajectory_dashboards.presentation_v1.model import load, layout_for, EXAMPLES, deduplicate_claims
from trajectory_dashboards.presentation_v1.render import render
from trajectory_dashboards.presentation_v1.charts import segments, num, observation, references


def example(case,method='compact_a'):
    return load(f'artifacts/stage6/comparison/{method}/{case}/accepted','Anonymous case')


@pytest.mark.parametrize('slug,label,method,case',EXAMPLES)
def test_saved_values_windows_units_counts_and_provenance_are_copied(slug,label,method,case,tmp_path):
    m=example(case,method);render(m,tmp_path)
    original=json.loads((Path(m['source'])/'evidence.json').read_text())
    exported=json.loads((tmp_path/'presentation.json').read_text())
    assert exported['evidence']==original
    assert len(m['provenance']['claims'])==len(m['bound']['claims'])
    for c in m['claims']:
        for index in c['original_indices']:
            assert m['bound']['claims'][index]['text']==c['original_text']
    for chart in (tmp_path/'charts').glob('*.svg'):
        tree=ET.fromstring(chart.read_text());data=json.loads(tree.find('{http://www.w3.org/2000/svg}metadata').text)
        if 'evidence_id' in data:
            e=original[data['evidence_id']]
            for key in ('trajectory','observation_status','assessment_status'):
                if key in data:
                    assert data[key]==e[key]
        for record in data.get('records',[]):
            e=original[record['evidence_id']]
            for key in ('summary','feature','window','reference_window'):
                assert record[key]==e[key]


def test_layout_uses_semantics_not_case_ids():
    for case in ('s6_01','s6_05','s6_09','s6_17'):
        m=example(case);expected=m['layout'];changed=deepcopy(m)
        changed['question'].update(question_id='not-a-task',person_id=-1,kind='unseen')
        assert layout_for(changed['claims'],changed['evidence'])==expected


def test_personal_only_selection_does_not_become_a_recent_peer_answer(tmp_path):
    agent=example('s6_15');baseline=example('s6_15','baseline')
    assert len(agent['comparison_ids'])==2
    assert all(agent['evidence'][eid]['window']==[0,3] for eid in agent['comparison_ids'])
    assert len(baseline['comparison_ids'])==1
    assert baseline['evidence'][baseline['comparison_ids'][0]]['window']==[10,11]
    # The recent evidence exists in the accepted dictionary via personal selections.
    assert any(e['window']==[10,11] for e in agent['evidence'].values())
    render(agent,tmp_path)
    text=(tmp_path/'figure.html').read_text()
    assert 'Peer comparison unavailable' not in text
    assert 'Personal comparison unavailable' in text
    assert 'data-answer="peer"' in text
    assert 'numerical validity does not establish completeness' in text


def test_missing_zero_ineligible_and_unknown_are_distinct():
    m=example('s6_09');e=next(e for e in m['evidence'].values() if e['feature']=='clicks_per_eligible_day')
    rows=e['observation_status']
    assert all(r['value']==0 and r['observation_status']=='zero_recorded_activity' for r in rows[:4])
    assert all(r['value'] is None and r['observation_status']=='ineligible' for r in rows[4:])
    assert num(0)=='0.00' and num(None)=='Unavailable'
    assert 'unknown' in observation(e) and e['summary']['focal_mean'] is None
    fixture=[{'week':0,'focal_value':0},{'week':1,'focal_value':None},{'week':2,'focal_value':2}]
    assert segments(fixture,'focal_value')==[[fixture[0]],[fixture[2]]]


def test_assessment_status_is_not_reinterpreted_as_feature_zero():
    m=example('s6_09');e=next(e for e in m['evidence'].values() if e['feature']=='scheduled_no_submission')
    row=e['observation_status'][2]
    assert row['observation_status']=='zero_recorded_activity' and row['value']==1
    svg=observation(e)
    assert 'click-record state' in svg and 'not a measure of effort' in svg


def test_exact_personal_duplicates_keep_multiplicity_but_distinct_intervals_do_not_merge():
    m=example('s6_01')
    assert len(m['claims'])==3
    personal=next(c for c in m['claims'] if c['template']=='personal_change')
    assert personal['original_indices']==[0,2] and len(personal['evidence_ids'])==2
    changed=deepcopy(m['evidence']);changed[personal['evidence_ids'][1]]['summary']['recent_mean']+=1
    assert len(deduplicate_claims(m['spec'],m['bound'],m['provenance'],changed))==4
    m=example('s6_15')
    assert len([c for c in m['claims'] if c['template']=='comparison'])==2


def test_reference_states_keep_focal_measure_window_scale_and_interval_scope():
    m=example('s6_05');ee=[m['evidence'][eid] for eid in m['comparison_ids']]
    assert m['switchable']
    states=[]
    for e in ee:
        tree=ET.fromstring(references(ee,e['evidence_id']))
        states.append(json.loads(tree.find('{http://www.w3.org/2000/svg}metadata').text))
    assert {tuple(x['x_domain']) for x in states}=={(0,8)}
    assert {tuple(e['window']) for e in ee}=={(8,11)}
    assert {e['summary']['focal_mean'] for e in ee}=={3.5}
    assert {tuple(e['reference_window']) for e in ee}=={(8,11),(0,3)}
    assert all('no interval for a focal contrast' in e['uncertainty']['scope'] for e in ee)


def test_changed_saved_evidence_is_rejected(tmp_path):
    source=Path('artifacts/stage6/comparison/compact_a/s6_01/accepted')
    for name in ('question.json','spec.json','evidence.json','bound.json','selection_provenance.json'):
        shutil.copyfile(source/name,tmp_path/name)
    evidence=json.loads((tmp_path/'evidence.json').read_text())
    next(iter(evidence.values()))['summary']['peer_ci_high']+=3
    (tmp_path/'evidence.json').write_text(json.dumps(evidence))
    with pytest.raises(ValueError,match='changed since numerical validation'):
        load(tmp_path,'Anonymous')

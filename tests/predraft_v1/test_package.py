"""Focused scientific/source boundaries for the pre-draft deliverables."""
import csv,json,hashlib,zipfile
from pathlib import Path
import xml.etree.ElementTree as ET
from trajectory_dashboards.presentation_v1.model import load
from trajectory_dashboards.predraft_v1.render import render,focused
from trajectory_dashboards.predraft_v1 import charts
R=Path('artifacts/predraft_v1')
def read(p):return json.loads(Path(p).read_text())
def model(case,method='compact_a'):return load(f'artifacts/stage6/comparison/{method}/{case}/accepted','Anonymous')
def meta(s):return json.loads(ET.fromstring(s).find('{http://www.w3.org/2000/svg}metadata').text)

def test_failure_excerpt_preserves_selected_wrong_window_and_personal_insufficiency(tmp_path):
    a=model('s6_15');b=model('s6_15','baseline');render(a,tmp_path/'a');render(b,tmp_path/'b')
    ah,_=focused(a,tmp_path/'a');bh,_=focused(b,tmp_path/'b')
    assert 'Personal comparison unavailable' in ah and 'Personal comparison unavailable' in bh
    assert 'Peer comparison unavailable' not in ah and 'Peer comparison unavailable' in bh
    for e in a['evidence'].values():
        if e['window']==[10,11]:assert f'data-answer="peer" data-evidence="{e["evidence_id"]}"' not in ah
    assert all(a['evidence'][eid]['window']==[0,3] for eid in a['comparison_ids'])
    assert len(a['comparison_ids'])==2  # Different intervals must not be collapsed.

def test_rounding_and_measurement_semantics_preserved(tmp_path):
    m=model('s6_01');render(m,tmp_path);content,_=focused(m,tmp_path)
    for v in ['14.07','3.54','−10.54','−0.68']:assert v in content
    assert 'Difference calculated before rounding' in content
    assert 'Uncertainty for the change was not estimated' in content
    assert round(3.54-14.07,2)==-10.53  # Hand check explains visible rounding difference.
    assert read(tmp_path/'presentation.json')['evidence']==read(Path(m['source'])/'evidence.json')

def test_reference_states_share_focal_scale_but_preserve_period_and_counts():
    m=model('s6_05');records=[m['evidence'][eid] for eid in m['comparison_ids']]
    states={e['reference']:meta(charts.reference(records,e['evidence_id'])) for e in records}
    assert {tuple(x['x_domain']) for x in states.values()}=={(0,8)}
    assert {tuple(x['window']) for x in states.values()}=={(8,11)}
    assert {x['summary']['focal_mean'] for x in states.values()}=={3.5}
    assert states['course']['reference_window']==[8,11] and states['early_stage']['reference_window']==[0,3]
    assert [e['people'] for e in records if e['reference']=='course']==[1024]
    assert [e['people'] for e in records if e['reference']=='early_stage']==[1128]

def test_observation_zero_and_ineligible_do_not_become_equal():
    m=model('s6_09');e=next(e for e in m['evidence'].values() if e['feature']=='clicks_per_eligible_day');s=meta(charts.observation(e))
    assert [r['observation_status'] for r in s['observation_status']]==['zero_recorded_activity']*4+['ineligible']*4
    assert [r['value'] for r in s['observation_status']]==[0]*4+[None]*4
    assert e['summary']['focal_mean'] is None and e['summary']['focal_observations']==0
    assert m['selection_status']=='agent repaired'

def test_results_categories_agree_with_frozen_endpoints_and_expected_counts():
    source=read('artifacts/stage6/reports/per_case.json');result=read(R/'results_categories.json');assert len(source)==96
    assert result['counts']=={'baseline':[24,0,0,0],'compact_a':[18,3,1,2],'derived_b':[14,1,9,0],'binding_c':[11,4,6,3]}
    for method,counts in result['counts'].items():
        rows=[r for r in source if r['condition']==method]
        selected={r['question_id'] for r in rows if r.get('complete_method_selected_coverage')}
        visible={r['question_id'] for r in rows if r['complete_requested_coverage']}
        accepted={r['question_id'] for r in rows if r['valid_after_repair']}
        assert selected<=visible<=accepted
        assert counts==[len(selected),len(visible-selected),len(accepted-visible),24-len(accepted)]
    for n in range(17,21):assert next(r for r in result['records'] if r['condition']=='derived_b' and r['question_id']==f's6_{n}')['category']=='accepted_incomplete'

def test_all_slots_and_blank_independent_forms():
    packet=read(R/'human_review/packet.json')['records'];mapping=read(R/'human_review/coordinator_private/reconciliation.json')['mapping'];assert len(packet)==len(mapping)==96
    assert len({(r['condition'],r['question_id']) for r in mapping})==96
    assert sum(r['output']=='no accepted dashboard' for r in packet)==5
    assert all(v is None for r in packet for v in r['review'].values())
    assert all(not {'covered','outcome','origin'}&a.keys() for r in packet for a in r['analytical_requirements'])
    for reviewer in ['reviewer_1','reviewer_2']:
        form=read(R/f'human_review/{reviewer}.json');assert form['reviewer'] is None and len(form['records'])==96
        assert all(v is None for r in form['records'] for v in r['ratings'].values())
        assert all(v is None for r in form['records'] for a in r['requested_answers'] for k,v in a.items() if k!='requirement_id')
        for suffix in ['', '_answers']:
            rows=list(csv.DictReader((R/f'human_review/{reviewer}{suffix}.csv').open()))
            assert all(v=='' for r in rows for k,v in r.items() if k not in ['review_id','requirement_id'])
    assert all(v is None for r in read(R/'human_review/adjudication.json')['records'] for k,v in r.items() if k!='review_id')

def test_official_template_bytes_and_actual_dimensions():
    t=R/'template';m=read(t/'manifest.json')
    with zipfile.ZipFile(t/'SCITEPRESS_Conference_Latex.zip') as z:
        for name in z.namelist():assert z.read(name)==(t/'official'/name).read_bytes()
    assert m['textwidth_mm']==158.0134 and m['columnsep_mm']==8
    for p in (R/'proof').glob('*.sty'):assert p.read_bytes()==(t/'official'/p.name).read_bytes()

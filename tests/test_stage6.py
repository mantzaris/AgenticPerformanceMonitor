import copy, json
from pathlib import Path
import pytest
from trajectory_dashboards.common import read_json,file_hash
from trajectory_dashboards.stage2.core import seal
from trajectory_dashboards.stage5.core import Engine as OldEngine
from trajectory_dashboards.stage5 import adapter as old_adapter
from trajectory_dashboards.stage4.evaluation import evaluate
from trajectory_dashboards.stage6 import adapter
from trajectory_dashboards.stage6.binding import (identity, catalogue, derived, resolve, compile_selection,
                                                 DerivedAction, BindingAction)


@pytest.fixture(scope='module')
def known():
    engine=OldEngine()
    tasks=read_json('artifacts/stage5/tasks/manifest.json')['tasks']
    q=next(t['question'] for t in tasks if t['question']['question_id']=='s5_07')
    records=read_json('artifacts/stage5/comparison/qwen14b_semantic/s5_07/tool_results.json')
    recent=next(e for e in records.values() if e['reference']=='course' and e['request']['window']=='recent')
    return engine,q,records,recent


@pytest.mark.parametrize('change',[('reference=course','reference=same_prior_attempt'),('focal=2:3','focal=1:3'),('peer_comparison','personal_change')])
def test_mismatched_binding_rejected_without_substitution(known,change):
    eng,q,records,e=known
    handle=identity(q,e,'peer_comparison').replace(*change)
    with pytest.raises(ValueError,match='Unresolved binding'):
        compile_selection(eng,q,{'answers':[{'identity':handle}]},records,'binding_c')


@pytest.mark.parametrize('condition',['derived_b','binding_c'])
def test_personal_selection_is_still_incomplete_and_adds_no_peer(known,condition,monkeypatch):
    eng,q,records,e=known
    monkeypatch.setattr(eng,'analyze',lambda *a:pytest.fail('Compiler must not request an analysis'))
    selection={'kind':'personal_change','evidence_id':e['evidence_id']} if condition=='derived_b' else {'identity':identity(q,e,'personal_change')}
    spec,proof=compile_selection(eng,q,{'answers':[selection]},records,condition)
    assert not any(c.template=='comparison' for c in spec.claims)
    score=evaluate(q,spec.model_dump(),records,records,proof,True)
    assert not score['complete_requested_coverage'] and score['retrieved_but_omitted']==['course_comparison']
    assert proof['conclusion']['origin']=='compiler_supplied'
    assert all(p['origin']=='method_selected' for c,p in zip(spec.claims,proof['claims']) if c.template=='personal_change')


def test_personal_aliases_require_exact_temporal_numerical_agreement(known):
    eng,q,records,e=known
    handle=identity(q,e,'personal_change')
    assert 'reference=' not in handle
    eid,kind,record,aliases=resolve(q,handle,records)
    assert len(aliases)==4 and eid==min(records) and kind=='personal_change'
    changed=copy.deepcopy(records);changed[e['evidence_id']]['summary']['recent_mean']=12.5
    with pytest.raises(ValueError,match='Ambiguous binding'):resolve(q,handle,changed)
    forged=seal(changed[e['evidence_id']]).model_dump()
    changed.pop(e['evidence_id']);changed[forged['evidence_id']]=forged
    with pytest.raises(ValueError,match='summary.recent_mean: expected None'):
        compile_selection(eng,q,{'answers':[{'identity':handle}]},changed,'binding_c')


def test_support_and_unavailable_measurements_are_separate(known):
    eng,q,records,e=known
    assert derived(e,'peer_comparison')=={'support':'insufficient_evidence','scope':'peer','answer_state':'supported_insufficiency'}
    assert derived(e,'personal_change')['scope']=='personal'
    assert derived(e,'measurement_limit')=={'support':'describe','scope':'measurement','answer_state':'unavailable_measurement'}
    baseline=next(x for x in records.values() if x['reference']=='course' and x['request']['window']=='baseline')
    assert derived(baseline,'peer_comparison')['support']=='describe'
    for condition,selection in [('derived_b',{'kind':'peer_comparison','evidence_id':e['evidence_id']}),('binding_c',{'identity':identity(q,e,'peer_comparison')})]:
        spec,proof=compile_selection(eng,q,{'answers':[selection]},records,condition)
        assert proof['semantic_answer']['answers'][0]['support']=='insufficient_evidence'
        assert proof['resolved_bindings'][0]['derived_metadata']['scope']=='peer'


def test_model_cannot_supply_redundant_metadata(known):
    _,q,_,e=known
    for cls,sel in [(DerivedAction,{'kind':'peer_comparison','evidence_id':e['evidence_id']}),(BindingAction,{'identity':identity(q,e,'peer_comparison')})]:
        with pytest.raises(ValueError):cls.model_validate({'action':'final','answers':[{**sel,'support':'describe'}]})
        with pytest.raises(ValueError):cls.model_validate({'action':'final','answers':[sel],'conclusion':{'scope':'personal'}})


def test_a_messages_exactly_unchanged_and_bc_same_catalogue(known,tmp_path,monkeypatch):
    eng,q,_,e=known
    monkeypatch.setattr(adapter,'event',lambda v:None);monkeypatch.setattr(old_adapter,'event',lambda v:None)
    first=[]
    def capture(msg,*args):first.append(copy.deepcopy(msg));raise RuntimeError('no model called')
    with pytest.raises(RuntimeError):old_adapter.episode(eng,q,'semantic',capture,tmp_path/'old','qwen14b')
    with pytest.raises(RuntimeError):adapter.episode(eng,q,'compact_a',capture,tmp_path/'a')
    assert first[0]==first[1]
    tool_messages=[];initial=[]
    for condition in ['derived_b','binding_c']:
        def fake(msg,*args):
            if len(msg)==2:
                initial.append(copy.deepcopy(msg))
                return json.dumps({'action':'analyze','requests':[e['request']]}),{}
            tool_messages.append(json.loads(next(m['content'] for m in msg if m['role']=='tool')))
            raise RuntimeError('mechanical fixture, no model called')
        with pytest.raises(RuntimeError):adapter.episode(eng,q,condition,fake,tmp_path/condition)
    assert tool_messages[0]==tool_messages[1]
    for messages in initial:
        payload=json.loads(messages[1]['content']);assert not {'rubric','required_answers','independent_facts'}&payload.keys()
    assert catalogue(q,e)==tool_messages[0][0]['result']['available_answers']


def test_historical_files_and_scientific_components_unchanged():
    inventory=read_json('artifacts/stage6/checks/history_inventory.json')['files']
    assert all(file_hash(p)==h for p,h in inventory.items())
    assert adapter.evaluate is evaluate

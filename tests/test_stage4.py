"""Focused semantic meaning, attribution, shared scoring and bounded-path checks."""
import json
import pytest
from trajectory_dashboards.common import read_json, file_hash
from trajectory_dashboards.stage2.core import Question, Request, seal
from trajectory_dashboards.stage2.integrity import validate, reference_conclusion
from trajectory_dashboards.stage3.evaluation import evaluate as old_evaluate
from trajectory_dashboards.stage4.core import Engine
from trajectory_dashboards.stage4.semantic import Answer, SemanticAction, compile_answer, full_provenance
from trajectory_dashboards.stage4.evaluation import evaluate
from trajectory_dashboards.stage4.display import render, replay
from trajectory_dashboards.stage4 import agents


@pytest.fixture(scope='module')
def data():
    engine=Engine()
    qs={t['question']['kind']:Question.model_validate(t['question']) for t in read_json('artifacts/stage4/tasks/construction.json')['episodes']}
    records={}
    for kind,q in qs.items():
        features=['nonbanked_submissions','scheduled_no_submission'] if kind=='assessment_availability' else ['clicks_per_eligible_day']
        records[kind]=[engine.analyze(q,Request(question_id=q.question_id,feature=f,reference='course')) for f in features]
    return engine,qs,records


def selection(e,kind='peer_comparison',support='describe'):
    return {'kind':kind,'evidence_id':e.evidence_id,'support':support}


def compile_one(data,kind='personal_change',intent='personal_change',support='describe'):
    engine,qs,records=data;e=records[kind][0]
    spec,p=compile_answer(engine,qs[kind],{'answers':[selection(e,intent,support)]},{e.evidence_id:e})
    return qs[kind],e,spec,p


def test_personal_does_not_insert_peer_answer(data):
    q,e,s,p=compile_one(data)
    assert [c.template for c in s.claims]==['personal_change']
    assert not any(x.kind=='comparison' for x in s.panels)
    score=evaluate(q.model_dump(),s.model_dump(),{e.evidence_id:e},{e.evidence_id:e},p)
    assert not score['complete_requested_coverage']
    assert score['retrieved_but_omitted']==['course_comparison']


def test_peer_does_not_insert_personal_answer(data):
    q,e,s,p=compile_one(data,intent='peer_comparison')
    score=evaluate(q.model_dump(),s.model_dump(),{e.evidence_id:e},{e.evidence_id:e},p)
    assert score['retrieved_but_omitted']==['personal_change']


def test_only_explicit_evidence_selected_and_no_dispatch(data,monkeypatch):
    engine,qs,records=data;q=qs['personal_change'];a=records[q.kind][0]
    b=engine.analyze(q,Request(question_id=q.question_id,feature='active_days',reference='course'))
    monkeypatch.setattr(engine,'analyze',lambda *args,**kwargs:pytest.fail('compiler dispatched an analysis'))
    s,p=compile_answer(engine,q,{'answers':[selection(a,'personal_change')]},{a.evidence_id:a,b.evidence_id:b})
    assert s.evidence_ids==[a.evidence_id] and p['additional_analyses']==0


def test_insufficient_estimate_rejected_and_scoped_answer_supported(data):
    engine,qs,records=data;q=qs['insufficient_support'];e=records[q.kind][0]
    assert e.status=='insufficient_evidence'
    with pytest.raises(ValueError,match='requires insufficient_evidence'):
        compile_answer(engine,q,{'answers':[selection(e)]},{e.evidence_id:e})
    answers=[selection(e,k,'insufficient_evidence') for k in ['peer_comparison','personal_change']]
    s,p=compile_answer(engine,q,{'answers':answers},{e.evidence_id:e})
    score=evaluate(q.model_dump(),s.model_dump(),{e.evidence_id:e},{e.evidence_id:e},p)
    assert score['complete_method_selected_coverage']
    assert set(score['scoped_insufficiency_items'])=={'personal_change','course_comparison'}


def test_unsupported_insufficiency_rejected(data):
    with pytest.raises(ValueError,match='requires describe'):
        compile_one(data,intent='peer_comparison',support='insufficient_evidence')


def test_unknown_evidence_and_generated_numbers_rejected(data):
    engine,qs,records=data;q=qs['personal_change']
    with pytest.raises(ValueError,match='Unknown evidence'):
        compile_answer(engine,q,{'answers':[{'kind':'peer_comparison','evidence_id':'invented'}]}, {})
    with pytest.raises(ValueError):
        Answer.model_validate({'answers':[{'kind':'peer_comparison','evidence_id':'x','value':100}]})


def test_wrong_reference_conclusion_rejected(data):
    engine,qs,records=data;q=qs['reference_sensitivity']
    es=[engine.analyze(q,Request(question_id=q.question_id,feature='clicks_per_eligible_day',reference=r)) for r in ['course','early_stage']]
    expected=reference_conclusion(es);wrong='same_direction' if expected=='direction_differs' else 'direction_differs'
    with pytest.raises(ValueError,match='Unsupported semantic'):
        compile_answer(engine,q,{'answers':[selection(e) for e in es],'conclusion':{'kind':wrong,'scope':'peer','evidence_ids':[e.evidence_id for e in es]}},{e.evidence_id:e for e in es})


def test_unselected_conclusion_scope_rejected(data):
    engine,qs,records=data;q=qs['personal_change'];e=records[q.kind][0]
    with pytest.raises(ValueError,match='Conclusion scope'):
        compile_answer(engine,q,{'answers':[selection(e)],'conclusion':{'kind':'same_direction','scope':'peer','evidence_ids':['invented']}},{e.evidence_id:e})


def test_context_credit_is_compiler_not_investigation(data):
    engine,qs,records=data;q=qs['assessment_availability'];es=records[q.kind]
    s,p=compile_answer(engine,q,{'answers':[selection(e) for e in es]},{e.evidence_id:e for e in es})
    score=evaluate(q.model_dump(),s.model_dump(),{e.evidence_id:e for e in es},{e.evidence_id:e for e in es},p)
    assert score['complete_requested_coverage'] and not score['complete_method_selected_coverage']
    assert set(score['compiler_supplied_answers'])=={'assessment_records','measurement_availability'}
    assert all(x['origin']=='method_selected' for c,x in zip(s.claims,p['claims']) if c.template in {'comparison','personal_change'})


def test_explicit_context_gets_selected_credit(data):
    engine,qs,records=data;q=qs['assessment_availability'];es=records[q.kind]
    intents=[selection(e) for e in es]+[selection(es[0],k) for k in ['assessment_status','measurement_limit']]
    s,p=compile_answer(engine,q,{'answers':intents},{e.evidence_id:e for e in es})
    score=evaluate(q.model_dump(),s.model_dump(),{e.evidence_id:e for e in es},{e.evidence_id:e for e in es},p)
    assert score['complete_method_selected_coverage']


def test_rehashed_source_corruption_rejected(data):
    engine,qs,records=data;q=qs['personal_change'];e=records[q.kind][0]
    bad=e.model_dump();bad['trajectory'][0]['focal_value']+=1;bad=seal(bad)
    with pytest.raises(ValueError,match='trusted source'):
        compile_answer(engine,q,{'answers':[selection(bad)]},{bad.evidence_id:bad})


def test_full_interface_scores_match_historical_semantics(data):
    q,e,s,p=compile_one(data)
    full=full_provenance(s);ev={e.evidence_id:e};new=evaluate(q.model_dump(),s.model_dump(),ev,ev,full)
    old=old_evaluate(q.model_dump(),s.model_dump(),ev,ev)
    for key in ['complete_requested_coverage','complete_method_selected_coverage','answer_fraction','compiler_supplied_answers']:
        assert new[key]==old[key]


def test_common_policy_and_no_map_schema():
    prompts=read_json('configs/stage4_prompts.json')
    assert prompts['generic_policy']==read_json('configs/stage3_prompts.json')['generic']
    assert 'request_map' not in SemanticAction.model_json_schema()['properties']
    assert 'request_map' not in agents.FullAction.model_json_schema()['properties']


@pytest.mark.parametrize('method',['full_spec','semantic'])
def test_real_dispatch_loop_with_scripted_model_and_replay(data,tmp_path,monkeypatch,method):
    engine,qs,records=data;q=qs['personal_change'];calls=[]
    monkeypatch.setattr(agents,'event',lambda x:None)
    def generate(messages,qid,m,phase,case):
        calls.append(messages.copy())
        if len(calls)==1:
            raw={'action':'analyze','requests':[Request(question_id=qid,feature='clicks_per_eligible_day',reference='course').model_dump()]}
        else:
            tool=next(json.loads(x['content']) for x in messages if x['role']=='tool')[0]['result']
            eid=tool['evidence_id'];e=records[q.kind][0]
            if method=='semantic':raw={'action':'final','answers':[selection(e,'peer_comparison'),selection(e,'personal_change')]}
            else:
                s,_=compile_answer(engine,q,{'answers':[selection(e,'peer_comparison'),selection(e,'personal_change')]},{eid:e})
                raw={'action':'final','specification':s.model_dump()}
        return json.dumps(raw),{'prompt_tokens':1,'completion_tokens':1}
    result=agents.episode(engine,q,method,generate,tmp_path/'case')
    assert result['status']=='agent_generated_and_accepted' and result['generations']==2 and result['tool_calls_attempted']==1
    assert all('required_answers' not in x['content'] and 'independent_facts' not in x['content'] for x in calls[0])
    replay(engine,tmp_path/'case/accepted',tmp_path/'replay')
    for name in ['bound.json','chart.vl.json','dashboard.svg','selection_provenance.json']:
        assert file_hash(tmp_path/'case/accepted'/name)==file_hash(tmp_path/'replay'/name)

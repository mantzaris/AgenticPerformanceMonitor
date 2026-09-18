"""Small synthetic semantic fixtures; never pilot evidence."""
import copy, json
from pathlib import Path
import pytest
from trajectory_dashboards.stage3.evaluation import assess_item, evaluate, requirements
from trajectory_dashboards.stage3.core import Action, Engine


def record(feature='clicks_per_eligible_day', reference='course', peer='supported', personal='supported', window='recent'):
    return {'feature':feature,'reference':reference,'request':{'window':window},'status':peer,
            'window':[8,11] if window=='recent' else [0,3],'reference_window':[0,3] if reference=='early_stage' else [8,11],
            'summary':{'personal_status':personal,'baseline_window':[0,3],'recent_window':[8,11],'focal_mean':2.0}}


def spec(claims=(), panels=(), conclusion='descriptive', ids=('e',)):
    return {'evidence_ids':list(ids),'claims':[{'template':a,'evidence_id':b} for a,b in claims],
            'panels':[{'kind':a,'evidence_id':b} for a,b in panels],'conclusion':conclusion}


def item(category='peer', **kw):
    return {'category':category,'features':['clicks_per_eligible_day'],'reference':'course' if category=='peer' else None,'window':'recent',**kw}


@pytest.mark.parametrize('form',['claim','chart'])
def test_equivalent_supported_peer_answers(form):
    s=spec(claims=[('comparison','e')] if form=='claim' else [],panels=[('comparison','e')] if form=='chart' else [])
    assert assess_item(item(),s,{'e':record()})['covered']


def test_irrelevant_template_and_trajectory_are_not_window_answer():
    s=spec(claims=[('measurement_limits','e')],panels=[('trajectory','e')])
    assert not assess_item(item(),s,{'e':record()})['covered']


def test_supported_unique_insufficiency_conclusion_is_credited():
    assert assess_item(item(),spec(conclusion='insufficient_evidence'),{'e':record(peer='insufficient_evidence')})['outcome']=='insufficient_evidence'


def test_unsupported_and_ambiguous_insufficiency_do_not_cover():
    s=spec(conclusion='insufficient_evidence')
    assert not assess_item(item(),s,{'e':record()})['covered']
    assert not assess_item(item(),s,{'e':record(peer='insufficient_evidence',personal='insufficient_evidence')})['covered']
    s['claims']=[{'template':'comparison','evidence_id':'e'}]
    assert assess_item(item(),s,{'e':record(peer='insufficient_evidence',personal='insufficient_evidence')})['covered']
    assert not assess_item(item('personal'),s,{'e':record(peer='insufficient_evidence',personal='insufficient_evidence')})['covered']


def test_global_insufficiency_is_reported_without_excusing_omissions():
    q={'question_id':'fixture','kind':'insufficient_support'}
    e={'e':record(peer='insufficient_evidence',personal='insufficient_evidence')}
    out=evaluate(q,spec(conclusion='insufficient_evidence'),e,e)
    assert out['global_supported_insufficiency']
    assert out['answer_fraction']==0 and not out['complete_requested_coverage']


def test_partially_answered_question_and_retrieved_omission():
    q={'question_id':'fixture','kind':'personal_change'}
    e={'e':record()}; s=spec(claims=[('comparison','e')])
    out=evaluate(q,s,e,e)
    assert out['answer_fraction']==0.5
    assert out['retrieved_but_omitted']==['personal_change']
    assert not out['missing_requested_analyses']


def test_irrelevant_extra_panels_cannot_raise_score():
    q={'question_id':'fixture','kind':'personal_change'};e={'e':record()}
    s=spec(claims=[('comparison','e')]); before=evaluate(q,s,e,e)
    s['panels']=[{'kind':'trajectory','evidence_id':'e'}]*4
    after=evaluate(q,s,e,e)
    assert before['answer_fraction']==after['answer_fraction']
    assert after['optional']['repeated_panel_signatures']==3


def test_reference_question_does_not_require_personal_history():
    q={'question_id':'p03','kind':'reference_sensitivity'}
    assert all(i['category']!='personal' for i in requirements(q,True))
    records={r:record(reference=r) for r in ['course','same_prior_attempt','early_stage']}
    s=spec(conclusion='same_direction',ids=tuple(records))
    assert evaluate(q,s,records,records,historical=True)['complete_requested_coverage']


def test_feature_ambiguity_is_historical_only():
    q={'question_id':'fixture','kind':'personal_change'}; e={'e':record(feature='active_days')}
    s=spec(claims=[('comparison','e'),('personal_change','e')])
    assert evaluate(q,s,e,e,historical=True)['complete_requested_coverage']
    assert not evaluate(q,s,e,e)['complete_requested_coverage']


def test_personal_summary_from_baseline_request_is_equivalent():
    assert assess_item(item('personal'),spec(claims=[('personal_change','e')]),{'e':record(window='baseline')})['covered']


def test_unavailable_measurement_provenance_is_not_agent_credit():
    out=assess_item(item('availability'),spec(),{'e':record()})
    assert out['origin']=='compiler_supplied' and out['outcome']=='unavailable_measurement'


def test_missing_analysis_separate_from_retrieved_but_omitted():
    q={'question_id':'fixture','kind':'assessment_availability'};e={'e':record()}
    out=evaluate(q,spec(),e,e)
    assert set(out['missing_requested_analyses'])=={'nonbanked_submissions','scheduled_no_submission'}
    assert 'assessment_records' in out['retrieved_but_omitted']


def test_map_is_typed_and_not_a_gold_checklist():
    a=Action.model_validate({'action':'analyze','requests':[{'question_id':'x','feature':'active_days','reference':'course'}], 'request_map':[{'request':'Recent activity','status':'uninvestigated'}]})
    assert a.request_map[0].evidence_ids==[]
    with pytest.raises(ValueError):
        Action.model_validate({**a.model_dump(),'request_map':[{'request':'x','status':'invented'}]})


def test_actual_loop_can_choose_next_analysis_after_a_result(tmp_path,monkeypatch):
    from trajectory_dashboards.stage3 import agents
    from trajectory_dashboards.stage2.methods import specification
    from trajectory_dashboards.common import read_json
    monkeypatch.setattr(agents,'event',lambda _:None)
    q=read_json('artifacts/stage3/tasks/manifest.json')['tasks'][0]['question']
    engine=Engine(); turns=[]
    def generate(messages,qid,method,phase,case):
        turns.append(messages.copy())
        if len(turns)<3:
            if len(turns)==2: assert any(m['role']=='tool' and 'summary' in m['content'] for m in messages)
            return json.dumps({'action':'analyze','requests':[{'question_id':qid,'feature':'clicks_per_eligible_day','reference':'course' if len(turns)==1 else 'same_prior_attempt'}]}),{}
        saved=read_json(case/'tool_results.json')
        from trajectory_dashboards.stage2.core import Evidence,Question
        records=[Evidence.model_validate(e) for e in saved.values()]
        s=specification(Question.model_validate(q),records)
        return json.dumps({'action':'final','specification':s.model_dump(),'request_map':[{'request':'Click rate versus history and peers','status':'answered','evidence_ids':s.evidence_ids}],'stopping_status':'complete'}),{}
    result=agents.episode(engine,q,'coverage_aware',generate,tmp_path/'case')
    assert result['status']=='agent_generated_and_accepted'
    assert result['tool_calls_executed']==2 and result['generations']==3
    assert result['subsequent_analysis_after_results']
    assert read_json(tmp_path/'case/request_state.json')['stopping_status']=='complete'

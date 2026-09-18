"""Focused changed boundaries, using construction data and hand-checkable fixtures."""
import copy
import math
from pathlib import Path
import pandas as pd
import pytest
from trajectory_dashboards.common import read_json,digest
from trajectory_dashboards.stage2.core import ROOT,Question,Request,Registry,seal
from trajectory_dashboards.stage2.backend import Engine
from trajectory_dashboards.stage2.integrity import validate_evidence,validate,reference_conclusion
from trajectory_dashboards.stage2.methods import deterministic,specification
from trajectory_dashboards.stage2.display import render,replay


@pytest.fixture(scope='module')
def engine():return Engine()


def question(index=0):return Question.model_validate(read_json(ROOT/'tasks/manifest.json')['tasks'][index]['question'])


@pytest.mark.parametrize('field', ['trajectory_mean','trajectory_count','trajectory_interval','summary_interval','window_label','unit','denominator','focal_value'])
def test_resealed_numerical_corruption_rejected(engine,field):
    q=question();e=engine.analyze(q,Request(question_id=q.question_id,feature='clicks_per_eligible_day',reference='course'))
    d=e.model_dump()
    if field=='trajectory_mean':d['trajectory'][0]['peer_mean']+=1
    if field=='trajectory_count':d['trajectory'][0]['peer_people']-=1;d['trajectory'][0]['peer_observations']-=1
    if field=='trajectory_interval':d['trajectory'][0]['peer_ci_low']+=1
    if field=='summary_interval':d['summary']['peer_ci_high']+=1
    if field=='window_label':d['reference_label']='AAA_2013J peers in weeks 0–3'
    if field=='unit':d['unit']='study hours'
    if field=='denominator':d['observations']+=1
    if field=='focal_value':d['observation_status'][0]['value']+=1
    tampered=seal(d)
    assert tampered.evidence_id!=e.evidence_id
    with pytest.raises(ValueError,match=r'evidence\.'):
        validate_evidence(engine,q,tampered)


def test_alternate_profile_and_future_invariance(engine):
    q=question(5);req=Request(question_id=q.question_id,feature='clicks_per_eligible_day',reference='early_stage')
    e=engine.analyze(q,req)
    assert e.summary['baseline_window']==[2,5] and e.window==[6,9] and e.cutoff_day==69
    assert max(r['end_day'] for r in e.trajectory)==69
    assert max(r['as_of_day'] for r in e.assessment_status)<=69
    changed=copy.copy(engine);changed.weekly=engine.weekly.copy()
    changed.weekly.loc[changed.weekly.end_day>69,'clicks_per_eligible_day']=123456
    assert changed.analyze(q,req).evidence_id==e.evidence_id
    validate_evidence(engine,q,e)
    bad=q.model_copy(update={'cutoff_day':83})
    with pytest.raises(ValueError,match='cutoff_day'):engine.analyze(bad,req)


def test_question_does_not_imply_changed_conclusion(engine):
    q=question(1);spec,ev,_=deterministic(engine,q)
    assert q.kind=='reference_sensitivity'
    assert spec.conclusion==reference_conclusion([ev[eid] for eid in spec.evidence_ids])
    if spec.conclusion=='same_direction':
        with pytest.raises(ValueError,match='conclusion'):
            validate(engine,q,spec.model_copy(update={'conclusion':'direction_differs'}),ev)
    # No policy-specific reference obligations in universal integrity.
    one=next(e for e in ev.values() if e.reference=='course')
    single=specification(q,[one])
    validate(engine,q,single,{one.evidence_id:one})


def test_actionable_panel_errors_and_unknown_evidence(engine):
    q=question(4);spec,ev,_=deterministic(engine,q)
    bad=spec.model_copy(update={'panels':[p for p in spec.panels if p.kind!='trajectory']})
    with pytest.raises(ValueError,match="missing kind='trajectory'"):validate(engine,q,bad,ev)
    bad=spec.model_copy(update={'panels':[p for p in spec.panels if p.kind!='assessment_status']})
    with pytest.raises(ValueError,match="requires kind='assessment_status'"):validate(engine,q,bad,ev)
    bad=spec.model_copy(update={'evidence_ids':['invented']})
    with pytest.raises(ValueError,match='unknown invented'):validate(engine,q,bad,ev)


def fixture_engine(engine):
    e=copy.copy(engine);e.registry=Registry();e.cfg=e.registry.cfg;e.cfg['minimum_peer_people']=2
    e.excluded={1};e.integrity_cache={}
    rows=[]
    # Unequal histories and nulls: expected recent peer mean=(10+20)/2=15.
    for person,values in {1:[2,4,None,None],2:[0,0,10,10],3:[4,4,None,20],4:[None]*4}.items():
        for week,value in enumerate(values):
            state='unknown' if person==4 else ('ineligible' if value is None else ('zero_recorded_activity' if value==0 else 'recorded_activity'))
            rows.append(dict(person_id=person,course='AAA_2013J',week=week,start_day=week*7,end_day=week*7+6,eligible_days=None if person==4 else (0 if value is None else 7),prior_attempt_group='first_attempt',observation_status=state,logging_completeness='unknown',score_status='withheld_release_time_unknown',clicks_per_eligible_day=value))
    e.weekly=pd.DataFrame(rows)
    e.assessments=engine.assessments.iloc[:0].copy()
    q=Question(question_id='fixture',kind='insufficient_support',text='Synthetic boundary fixture, never pilot evidence',person_id=1,course='AAA_2013J',profile='short',cutoff_day=27)
    return e,q


def test_hand_calculated_support_zero_unknown_ineligible(engine):
    e,q=fixture_engine(engine)
    r=e.analyze(q,Request(question_id=q.question_id,feature='clicks_per_eligible_day',reference='course'))
    assert r.summary['peer_mean']==15 and r.people==2 and r.observations==3
    assert r.summary['baseline_mean']==3 and r.summary['recent_mean'] is None
    assert r.summary['personal_change'] is None and r.summary['contrast'] is None
    assert r.status=='insufficient_evidence' and 1 not in r.peer_ids
    assert r.trajectory[0]['peer_mean']==2 and r.trajectory[2]['peer_mean']==10
    assert r.observation_status[2]['value'] is None and r.observation_status[2]['observation_status']=='ineligible'
    validate_evidence(e,q,r)
    # One-person support threshold: neither observation count nor mean disguises it.
    e.excluded={1,3};e.integrity_cache={}
    r=e.analyze(q,Request(question_id=q.question_id,feature='clicks_per_eligible_day',reference='course'))
    assert r.people==1 and r.summary['peer_ci_low'] is None
    validate_evidence(e,q,r)


def test_person_grouping_reserved_and_original_exclusion(engine):
    m=read_json(ROOT/'tasks/manifest.json')
    a,b=set(m['construction_people']),set(m['pilot_people'])
    assert len(a)==6 and len(b)==12 and not a&b
    assert not (a|b)&set(m['original_demo_people_excluded'])
    assert not (a|b)&set(read_json('artifacts/data/splits.json')['assignments']['reserved'])
    assert a|b <= engine.excluded
    for q in [question(0),question(1)]:
        e=engine.analyze(q,Request(question_id=q.question_id,feature='clicks_per_eligible_day',reference='course'))
        assert not set(e.peer_ids)&engine.excluded


def test_replay_and_displayed_chart_bindings(engine,tmp_path):
    q=question();spec,ev,_=deterministic(engine,q)
    render(engine,q,spec,ev,tmp_path/'one')
    replay(engine,tmp_path/'one',tmp_path/'two')
    assert read_json(tmp_path/'one/chart.vl.json')==read_json(tmp_path/'two/chart.vl.json')
    assert read_json(tmp_path/'one/bound.json')==read_json(tmp_path/'two/bound.json')
    chart=read_json(tmp_path/'one/chart.vl.json');e=ev[spec.evidence_ids[0]]
    tables=list(chart['datasets'].values())
    trajectory=next(t for t in tables if t and 'peer_ci_low' in t[0])
    assert trajectory==e.trajectory
    comparison=next(t for t in tables if t and 'series' in t[0])
    assert comparison[0]['value']==e.summary['focal_mean']
    assert comparison[1]['lo']==e.summary['peer_ci_low'] and comparison[1]['hi']==e.summary['peer_ci_high']


def test_registry_rejects_reversed_or_future_windows(tmp_path):
    from trajectory_dashboards.common import write_json
    cfg=Registry().cfg;cfg['profiles']['standard']['recent']=[8,12]
    write_json(tmp_path/'bad.json',cfg)
    with pytest.raises(ValueError,match='post-cutoff'):Registry(tmp_path/'bad.json')


def test_followup_recomputes_and_preserves_parent(engine,tmp_path):
    from trajectory_dashboards.common import file_hash
    from trajectory_dashboards.stage2.followup import followup
    parent=ROOT/'construction/baseline/c04/accepted'
    before={n:file_hash(parent/n) for n in ('spec.json','question.json','evidence.json')}
    child=followup(engine,parent,'early_stage','short',tmp_path)
    old=next(iter(read_json(parent/'evidence.json').values()))
    new=next(iter(read_json(child/'evidence.json').values()))
    assert old['status']=='insufficient_evidence' and new['status']=='supported'
    assert new['window']==[2,3] and new['reference_window']==[0,1]
    assert new['evidence_id']!=old['evidence_id'] and len(new['trajectory'])==4
    assert read_json(child/'link.json')['parent_question_id']=='c04'
    assert before=={n:file_hash(parent/n) for n in before}
    with pytest.raises(ValueError,match='admissible'):followup(engine,parent,'invented','short',tmp_path)

"""Task-level scoring, intentionally separate from universal numerical integrity."""
from pathlib import Path
from ..common import read_json,write_json,now
from .core import ROOT,Question,Request
from .integrity import independent_facts


PROHIBITED = ["Clicks establish effort, ability or study time", "Scores were known at submission", "Non-submission proves failure or lack of learning", "Earlier-stage peers are causally adjusted or fairer", "Bootstrap peer-mean interval is individual prediction uncertainty", "Reference sensitivity was found merely because it was requested", "Unavailable or ineligible weeks are observed zeros", "Development pilot establishes general superiority"]


def coverage_items(kind):
    items=[]
    feature='nonbanked_submissions' if kind=='assessment_availability' else 'clicks_per_eligible_day'
    refs=['course','same_prior_attempt','early_stage'] if kind in {'reference_sensitivity','alternate_windows'} else ['course']
    items.extend({'id':f'evidence:{feature}:{r}:recent','type':'evidence','feature':feature,'reference':r,'window':'recent'} for r in refs)
    if kind in {'personal_change','reference_sensitivity','insufficient_support','alternate_windows'}:
        items.append({'id':'personal_history_claim','type':'claim','template':'personal_change','feature':'clicks_per_eligible_day'})
    if kind in {'observation_limits','assessment_availability'}:
        for f in ('nonbanked_submissions','scheduled_no_submission'):
            if f!=feature: items.append({'id':f'evidence:{f}:course:recent','type':'evidence','feature':f,'reference':'course','window':'recent'})
        items.extend([{'id':'assessment_context_panel','type':'panel','kind':'assessment_status'}, {'id':'explicit_measurement_qualification','type':'claim','template':'measurement_limits','feature':None}])
    items.append({'id':'observation_context_panel','type':'panel','kind':'observation_status'})
    return items


def create_rubrics(engine):
    target=ROOT/'evaluator_only/rubrics.json'
    if target.exists(): raise ValueError('Rubrics already exist; never overwrite frozen answers')
    rubrics=[]
    for task in read_json(ROOT/'tasks/manifest.json')['tasks']:
        q=Question.model_validate(task['question'])
        items=coverage_items(q.kind)
        facts={}
        for item in items:
            if item['type']!='evidence': continue
            req=Request(question_id=q.question_id,feature=item['feature'],reference=item['reference'],window=item['window'])
            f=independent_facts(engine,q,req)
            facts[item['id']]={k:f[k] for k in ('feature','unit','reference','reference_label','window','reference_window','status','people','observations','summary')}
        primary=facts[next(iter(facts))]
        contrasts=[f['summary']['contrast'] for f in facts.values() if f['feature']=='clicks_per_eligible_day']
        valid=[c for c in contrasts if c is not None]
        signs={0 if c==0 else (1 if c>0 else -1) for c in valid}
        direction='insufficient observed support' if len(valid)!=len(contrasts) else ('different signs' if len(signs)>1 else 'same sign among available selected comparisons')
        interpretations=["Report computed descriptive magnitudes and denominators; no causal or significance claim.","A descriptive conclusion without claiming reference dependence is admissible if contextual comparisons remain visible.",f"Activity comparison direction: {direction}.","Grade-release time is unknown; no claim about marks or learning can be made."]
        if primary['status']=='insufficient_evidence' or primary['summary']['personal_status']=='insufficient_evidence':
            interpretations.append("Explicit insufficient evidence for the unsupported contrast is appropriate; retain available measurements and distinguish ineligibility from zero.")
        rubrics.append({'question_id':q.question_id,'subset':task['subset'],'synthetic':False,'question':q.text,'cutoff_day':q.cutoff_day,'allowed_information':'Only allowlisted development features with end_day <= cutoff; contemporaneous assessment status; no scores, outcomes, future withdrawal, raw generated code or external data.','facts':facts,'coverage_items':items,'acceptable_interpretations':interpretations,'prohibited_unsupported_claims':PROHIBITED,'required_context':['Exact focal and reference windows and distinct-person/person-week counts','Eligibility states and unknown logging completeness','Grade withholding and banked-assessment caveat','Pointwise peer-mean interval label; no interval for personal change/contrast'],'expected_primary_support':primary['status'],'expected_personal_support':primary['summary']['personal_status'],'external_review':'AWAITING independent human/scientific review; independent calculation is not independent human review'})
    write_json(target,{'version':'stage2-rubric-v1','created_utc':now(),'calculation_path':'Row-loop reducer and scalar-loop bootstrap in integrity.independent_facts; never calls production Engine.analyze','agent_visibility':'This file is never read into model messages or accessible through the tool interface.','rubrics':rubrics})


def score(result,case,rubric):
    """Failures remain in the denominator; fallback exports never count as acceptance."""
    valid=result.get('status') in {'agent_generated_and_accepted','agent_generated_and_repaired','deterministic_accepted'}
    evidence={}; spec={}
    if valid:
        spec=read_json(Path(case)/'accepted/spec.json')
        evidence=read_json(Path(case)/'accepted/evidence.json')
    checks=[]
    for item in rubric['coverage_items']:
        hit=False
        if valid and item['type']=='evidence':
            hit=any(e['feature']==item['feature'] and e['reference']==item['reference'] and e['request']['window']==item['window'] for e in evidence.values())
        if valid and item['type']=='claim':
            hit=any(c['template']==item['template'] and (item['feature'] is None or evidence[c['evidence_id']]['feature']==item['feature']) for c in spec['claims'])
        if valid and item['type']=='panel': hit=any(p['kind']==item['kind'] for p in spec['panels'])
        checks.append({'id':item['id'],'covered':hit})
    insufficient_expected=rubric['expected_primary_support']=='insufficient_evidence' or rubric['expected_personal_support']=='insufficient_evidence'
    appropriate=None
    if insufficient_expected:
        appropriate=valid and any(e['status']=='insufficient_evidence' or e['summary']['personal_status']=='insufficient_evidence' for e in evidence.values()) and any(c['template'] in {'comparison','personal_change'} for c in spec['claims'])
    return {**result,'task_id':rubric['question_id'],'subset':rubric['subset'],'valid_after_permitted_repair':valid,'numerical_integrity': 'PASS' if valid else 'NO ACCEPTED OUTPUT','coverage':checks,'coverage_fraction':sum(c['covered'] for c in checks)/len(checks),'all_task_context_covered':all(c['covered'] for c in checks),'omitted_context':[c['id'] for c in checks if not c['covered']],'unsupported_claims_in_accepted_output':0 if valid else None,'unsupported_claim_scope':'Controlled claim vocabulary and integrity checks; does not assess unconstrained natural-language reasoning or human usefulness. Invalid attempts remain in logs.','compiler_context_present':valid,'compiler_context_credit':'Displayed and reported separately; not evidence of agent-selected investigation','insufficient_expected':insufficient_expected,'appropriate_insufficiency':appropriate,'rubric_review_status':'awaiting external review'}

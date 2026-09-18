"""Unchanged answer scoring, plus offline binding diagnostics and provenance."""
import json
from pathlib import Path
from ..common import read_json
from ..stage2.integrity import validate
from ..stage3.evaluation import requirements, _retrieved
from ..stage4.evaluation import evaluate
from ..stage4.semantic import compile_answer
from ..stage5.reporting import error_categories as historical_categories
from .binding import compile_selection, resolve


def unsupported_selections(question, sequence, retrieved, condition):
    findings=[]
    for step in sequence:
        try:action=json.loads(step['raw_output'])
        except (ValueError,KeyError):continue
        if not isinstance(action,dict) or action.get('action')!='final' or not isinstance(action.get('answers'),list):continue
        for index,intent in enumerate(action['answers']):
            if not isinstance(intent,dict):continue
            accepted=step.get('stopping_decision')=='valid final specification'
            numeric={k:v for k,v in intent.items() if k in {'focal_mean','peer_mean','contrast','personal_change','value'} and isinstance(v,(int,float))}
            if numeric:findings.append({'turn':step['turn'],'answer_index':index,'type':'unbound_numeric_fields','fields':numeric,'accepted':accepted})
            support=intent.get('support','describe' if condition=='compact_a' else None)
            if support!='describe':continue
            eid,kind=intent.get('evidence_id'),intent.get('kind')
            if condition=='binding_c':
                try:eid,kind,_,_=resolve(question,intent.get('identity'),retrieved)
                except ValueError:continue
            if eid not in retrieved or kind not in {'peer_comparison','personal_change'}:continue
            e=retrieved[eid];status=e['status'] if kind=='peer_comparison' else e['summary']['personal_status']
            if status!='supported':findings.append({'turn':step['turn'],'answer_index':index,'type':'describe_on_unsupported_comparison','kind':kind,'evidence_id':eid,'accepted':accepted})
    return findings


def errors_for(sequence):
    out=[]
    for step in sequence:
        if 'validation_error' not in step:continue
        error=step['validation_error'];low=error.lower();tags=set(historical_categories(error))
        for phrase,tag in [('unresolved binding','unresolved_binding'),('ambiguous binding','ambiguous_binding'),
                           ('selected evidence coverage:','layout_or_claim_contract'),
                           ('specification.conclusion: selected results support','unsupported_conclusion'),
                           ('analytical request budget exceeded','tool_budget_denial')]:
            if phrase in low:tags.add(tag)
        out.append({'turn':step['turn'],'error':error,'categories':sorted(tags)})
    return out


def selection_mismatches(scored, spec, evidence):
    """Offline diagnostic, not an integrity constraint or model feedback.

    Reports observable alternatives selected for an unanswered peer/personal item;
    it does not infer intent, causal attribution, or automatically fix the answer.
    """
    findings=[]
    for item in scored['requested_answers']:
        if item['covered'] or item['category'] not in {'peer','personal'}:continue
        wanted='comparison' if item['category']=='peer' else 'personal_change'
        for claim in spec.get('claims',[]):
            e=evidence[claim['evidence_id']]
            if e['feature'] not in item['features']:continue
            tags=[]
            if claim['template']==wanted and item['category']=='peer':
                if e['request']['window']!=item['window']:tags.append('wrong_window_for_requested_answer')
                if e['reference']!=item['reference']:tags.append('wrong_reference_for_requested_answer')
            if claim['template'] in {'comparison','personal_change'} and claim['template']!=wanted:
                if item['category']=='personal' or (e['request']['window']==item['window'] and e['reference']==item['reference']):
                    tags.append('wrong_peer_personal_kind_for_requested_answer')
            if tags:findings.append({'requested_item':item['id'],'evidence_id':e['evidence_id'],
                                    'selected_template':claim['template'],'categories':tags})
    return findings


def score_case(engine, q, case, condition, metrics=()):
    case=Path(case);attempted=(case/'started.json').exists()
    result=read_json(case/'result.json') if (case/'result.json').exists() else {'status':'not_attempted_infrastructure_blocked','first_attempt_valid':False}
    valid=result['status'] in {'deterministic_accepted','agent_generated_and_accepted','agent_generated_and_repaired'}
    retrieved=read_json(case/'tool_results.json') if (case/'tool_results.json').exists() else {}
    spec,selected,proof={},{},{}
    if valid:
        accepted=case/'accepted'
        spec=read_json(accepted/'spec.json');selected=read_json(accepted/'evidence.json');proof=read_json(accepted/'selection_provenance.json')
        validate(engine,q,spec,selected)
        if condition!='baseline':
            rebuilt,expected=(compile_answer(engine,q,proof['semantic_answer'],retrieved) if condition=='compact_a' else
                              compile_selection(engine,q,proof['original_selection'],retrieved,condition))
            assert rebuilt.model_dump()==spec and proof==expected
            assert all(p['origin']=='method_selected' for c,p in zip(spec['claims'],proof['claims']) if c['template'] in {'comparison','personal_change'})
    scored=evaluate(q,spec,selected,retrieved,proof,valid)
    sequence=read_json(case/'sequence.json') if (case/'sequence.json').exists() else []
    errors=errors_for(sequence)
    # A authors support; B/C do not. An omitted support field in B is not a
    # model assertion of sufficient support. Count only prohibited explicit fields.
    unsupported=unsupported_selections(q,sequence,retrieved,condition)
    assert not any(x['accepted'] for x in unsupported)
    mm=[m for m in metrics if m['budget_partition']=='comparison' and m['question_id']==q['question_id'] and m['method']==condition]
    requests=read_json(case/'requests.json') if (case/'requests.json').exists() else [t['request'] for s in sequence for t in s.get('tool_results',[])]
    p=engine.registry.profile(q);signatures=[]
    for request in requests:
        rule=engine.cfg['references'][request['reference']];w=p[request.get('window','recent')]
        rw=p['baseline'] if rule['time']=='baseline' else w
        signatures.append((request['feature'],rule['group'],tuple(w),tuple(rw)))
    mismatches=selection_mismatches(scored,spec,selected)
    return {**result,**scored,'condition':condition,'family':q['kind'],'attempted':attempted,'valid_after_repair':valid,
            'numerical_integrity':'PASS' if valid else 'NO ACCEPTED OUTPUT','unsupported_accepted_quantitative_answers':0 if valid else None,
            'unsupported_quantitative_attempts_rejected':unsupported,'errors':errors,
            'error_categories':sorted({t for e in errors for t in e['categories']}),
            'selection_mismatches':mismatches,'selection_mismatch_categories':sorted({t for m in mismatches for t in m['categories']}),
            'oracle_retrieved_upper_bound':bool(retrieved) and all(_retrieved(i,retrieved) for i in requirements(q)),
            'redundant_equivalent_analyses':len(signatures)-len(set(signatures)),
            'generations':len(mm),'prompt_tokens':sum(m.get('prompt_tokens',0) for m in mm),
            'completion_tokens':sum(m.get('completion_tokens',0) for m in mm),'generation_seconds':sum(m['elapsed_seconds'] for m in mm),
            'peak_allocated_bytes':max((m.get('peak_allocated_bytes',0) for m in mm),default=0),
            'compiler_added_panels':sum(p['origin']=='compiler_supplied' for p in proof.get('panels',[])),
            'compiler_added_claims':sum(p['origin']=='compiler_supplied' for p in proof.get('claims',[])),
            'compiler_inserted_quantitative_claims':proof.get('inserted_comparison_or_personal_claims',0),
            'derived_metadata_records':len(proof.get('resolved_bindings',[])),
            'neutral_compiler_heading':proof.get('conclusion',{}).get('origin')=='compiler_supplied',
            'artifact_path':str(case)}

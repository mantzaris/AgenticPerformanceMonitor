"""Frozen Stage 4 scoring; all cases retained, no inference and no tuning."""
import csv,json
from collections import Counter
from trajectory_dashboards.common import read_json,write_json,now,digest
from trajectory_dashboards.stage2.integrity import validate
from trajectory_dashboards.stage3.evaluation import requirements,_retrieved
from trajectory_dashboards.stage4.core import ROOT,Engine
from trajectory_dashboards.stage4.evaluation import evaluate
from trajectory_dashboards.stage4.semantic import compile_answer
from diagnose_stage3 import error_tags


def main():
    out=ROOT/'reports';out.mkdir(parents=True,exist_ok=True)
    if (out/'per_case.json').exists():raise ValueError('Preserve frozen pilot scores; use a fresh reproduction workspace')
    engine=Engine();rows=[]
    metrics=[read_json(p) for p in (ROOT/'gpu/generations').glob('*.metadata.json')]
    for task in read_json(ROOT/'tasks/manifest.json')['tasks']:
        q=task['question'];qid=q['question_id']
        for method in ['baseline','full_spec','semantic']:
            case=ROOT/'pilot'/method/qid
            result=read_json(case/'result.json') if (case/'result.json').exists() else {'status':'not_attempted','first_attempt_valid':False}
            valid=result['status'] in {'deterministic_accepted','agent_generated_and_accepted','agent_generated_and_repaired'}
            retrieved=read_json(case/'tool_results.json') if (case/'tool_results.json').exists() else {}
            spec,selected,provenance={},{},{}
            if valid:
                a=case/'accepted';spec=read_json(a/'spec.json');selected=read_json(a/'evidence.json');provenance=read_json(a/'selection_provenance.json')
                validate(engine,q,spec,selected)
                if method=='semantic':
                    rebuilt,proof=compile_answer(engine,q,provenance['semantic_answer'],retrieved)
                    assert digest(rebuilt.model_dump())==digest(spec) and proof==provenance
                    assert all(p['origin']=='method_selected' for c,p in zip(spec['claims'],provenance['claims']) if c['template'] in {'comparison','personal_change'})
            scored=evaluate(q,spec,selected,retrieved,provenance,valid)
            seq=read_json(case/'sequence.json') if (case/'sequence.json').exists() else []
            errors=[{'turn':s['turn'],'error':s['validation_error'],'tags':error_tags(s['validation_error'])} for s in seq if 'validation_error' in s]
            semantic_errors=[e for e in errors if any(t in e['error'] for t in ['answers[','Unknown evidence','semantic reference','Conclusion scope','Insufficiency conclusion','Duplicate semantic','Descriptive conclusion','Reference conclusion'])]
            mm=[m for m in metrics if m['budget_partition']=='pilot' and m['question_id']==qid and m['method']==method]
            reqs=read_json(case/'requests.json') if (case/'requests.json').exists() else [t['request'] for s in seq for t in s.get('tool_results',[])]
            p=engine.registry.profile(q);signatures=[]
            for req in reqs:
                rule=engine.cfg['references'][req['reference']];win=p[req.get('window','recent')];rw=p['baseline'] if rule['time']=='baseline' else win
                signatures.append((req['feature'],rule['group'],tuple(win),tuple(rw)))
            row={**result,**scored,'question_id':qid,'family':q['kind'],'method':method,'valid_after_repair':valid,
                 'numerical_integrity':'PASS' if valid else 'NO ACCEPTED OUTPUT','unsupported_accepted_quantitative_answers':0 if valid else None,
                 'errors':errors,'structural_error_episode':any('structural_specification' in e['tags'] for e in errors),
                 'unsupported_or_semantic_error_episode':bool(semantic_errors) or any('substantive_or_unsupported' in e['tags'] for e in errors),
                 'semantic_errors':semantic_errors,'oracle_retrieved_upper_bound':bool(retrieved) and all(_retrieved(item,retrieved) for item in requirements(q)),
                 'redundant_equivalent_analyses':len(signatures)-len(set(signatures)),
                 'generations':len(mm),'prompt_tokens':sum(m.get('prompt_tokens',0) for m in mm),'completion_tokens':sum(m.get('completion_tokens',0) for m in mm),
                 'generation_seconds':sum(m['elapsed_seconds'] for m in mm),'cuda_event_seconds':sum(m.get('cuda_event_ms',0)/1000 for m in mm),
                 'finish_reasons':dict(Counter(m.get('finish_reason','failed') for m in mm)),
                 'compiler_added_panels':sum(p['origin']=='compiler_supplied' for p in provenance.get('panels',[])),
                 'compiler_added_claims':sum(p['origin']=='compiler_supplied' for p in provenance.get('claims',[])),
                 'compiler_inserted_substantive_comparisons_or_changes':provenance.get('inserted_comparison_or_personal_claims',0),
                 'selection_provenance_path':str(case/'accepted/selection_provenance.json') if valid else None}
            rows.append(row)
    summaries=[]
    for method in ['baseline','full_spec','semantic']:
        rr=[r for r in rows if r['method']==method]
        summaries.append({'method':method,'denominator':12,'first_final_valid':sum(r.get('first_attempt_valid',False) for r in rr),
            'valid_after_repair':sum(r['valid_after_repair'] for r in rr),'complete_visible':sum(r['complete_requested_coverage'] for r in rr),
            'complete_method_selected':sum(r['complete_method_selected_coverage'] for r in rr),
            'oracle_retrieved_upper_bound':sum(r['oracle_retrieved_upper_bound'] for r in rr),
            'missing_analysis_items':sum(len(r['missing_requested_analyses']) for r in rr),'retrieved_but_omitted_items':sum(len(r['retrieved_but_omitted']) for r in rr),
            'scoped_insufficient_items':sum(len(r['scoped_insufficiency_items']) for r in rr),
            'structural_error_episodes':sum(r['structural_error_episode'] for r in rr),'semantic_or_substantive_error_episodes':sum(r['unsupported_or_semantic_error_episode'] for r in rr),
            'compiler_supplied_answer_items':sum(len(r['compiler_supplied_answers']) for r in rr),
            'compiler_added_panels':sum(r['compiler_added_panels'] for r in rr),'compiler_added_boilerplate_claims':sum(r['compiler_added_claims'] for r in rr),
            'unsupported_accepted_quantitative_answers':sum(r['unsupported_accepted_quantitative_answers'] or 0 for r in rr),
            'tools':sum(r.get('tool_calls_attempted',0) for r in rr),'redundant_exact':sum(r.get('redundant_requests',0) for r in rr),'redundant_equivalent':sum(r['redundant_equivalent_analyses'] for r in rr),
            'generations':sum(r['generations'] for r in rr),'repairs':sum(r.get('repairs',0) for r in rr),'fallbacks':sum(r.get('fallback',False) for r in rr),
            'prompt_tokens':sum(r['prompt_tokens'] for r in rr),'completion_tokens':sum(r['completion_tokens'] for r in rr),
            'episode_seconds':sum(r.get('elapsed_seconds',0) for r in rr),'generation_seconds':sum(r['generation_seconds'] for r in rr),
            'cuda_event_seconds':sum(r['cuda_event_seconds'] for r in rr),'failed_questions':[r['question_id'] for r in rr if not r['valid_after_repair']]})
    pairs=[]
    for task in read_json(ROOT/'tasks/manifest.json')['tasks']:
        qid=task['question']['question_id'];a=next(r for r in rows if r['question_id']==qid and r['method']=='full_spec');b=next(r for r in rows if r['question_id']==qid and r['method']=='semantic')
        outcome=lambda x,y:'improved' if y and not x else ('regressed' if x and not y else ('unchanged_complete' if y else 'unchanged_incomplete'))
        pairs.append({'question_id':qid,'family':a['family'],'visible_outcome':outcome(a['complete_requested_coverage'],b['complete_requested_coverage']),
            'selected_outcome':outcome(a['complete_method_selected_coverage'],b['complete_method_selected_coverage']),
            'full_valid':a['valid_after_repair'],'compact_valid':b['valid_after_repair'],
            'full_complete':a['complete_requested_coverage'],'compact_complete':b['complete_requested_coverage'],
            'full_selected_complete':a['complete_method_selected_coverage'],'compact_selected_complete':b['complete_method_selected_coverage'],
            'both_retrieved_required_evidence':a['oracle_retrieved_upper_bound'] and b['oracle_retrieved_upper_bound'],
            'full_structural_error':a['structural_error_episode'],'compact_structural_error':b['structural_error_episode'],
            'tool_difference':b.get('tool_calls_attempted',0)-a.get('tool_calls_attempted',0),'latency_difference_seconds':b.get('elapsed_seconds',0)-a.get('elapsed_seconds',0)})
    events=[json.loads(s) for s in (ROOT/'model_ledger.jsonl').read_text().splitlines()];ends=[e for e in events if e['event']=='process_finished']
    partitions=dict(Counter(e['budget_partition'] for e in events if e['event']=='generation_started'))
    compact=next(s for s in summaries if s['method']=='semantic')
    comparison={'created_utc':now(),'summaries':summaries,'paired_visible':dict(Counter(p['visible_outcome'] for p in pairs)),
        'paired_method_selected':dict(Counter(p['selected_outcome'] for p in pairs)),
        'engineering_target':{'required_complete_visible':11,'denominator':12,'actual':compact['complete_visible'],'no_accepted_unsupported_quantitative':compact['unsupported_accepted_quantitative_answers']==0,'met':compact['complete_visible']>=11 and compact['unsupported_accepted_quantitative_answers']==0},
        'generation_partitions':partitions,'total_generations':sum(partitions.values()),'model_process_seconds':sum(e['elapsed_seconds'] for e in ends),'model_processes':ends,
        'unclosed_processes':sorted({e['process_id'] for e in events if e['event']=='process_started'}-{e['process_id'] for e in ends}),
        'interpretation':'Twelve development case units; paired interface comparison, not new task families, repeatability or held-out generalization. Oracle retrieval bounds are diagnostic only.'}
    write_json(out/'per_case.json',rows);write_json(out/'paired_cases.json',pairs);write_json(out/'comparison.json',comparison)
    columns=['method','question_id','family','status','first_attempt_valid','valid_after_repair','complete_requested_coverage','complete_method_selected_coverage','tool_calls_attempted','generations','repairs','prompt_tokens','completion_tokens','elapsed_seconds']
    with (out/'per_case.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=columns,extrasaction='ignore');w.writeheader();w.writerows(rows)
    print(json.dumps(comparison,indent=2))


if __name__=='__main__':main()

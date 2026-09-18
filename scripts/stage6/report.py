"""Frozen paired ablation report; all 96 method/case slots remain in denominator."""
import csv,json
from collections import Counter
from trajectory_dashboards.common import read_json,write_json,now
from trajectory_dashboards.stage6.core import ROOT,Engine,CONDITIONS,verify_freeze
from trajectory_dashboards.stage6.reporting import score_case
from trajectory_dashboards.stage5.reporting import paired_outcome


def main():
    verify_freeze();out=ROOT/'reports'
    if (out/'per_case.json').exists():raise ValueError('Preserve primary scores; use a fresh reproduction destination')
    engine=Engine();tasks=read_json(ROOT/'tasks/manifest.json')['tasks']
    metrics=[read_json(p) for p in (ROOT/'gpu/generations').glob('*.metadata.json')]
    rows=[score_case(engine,t['question'],ROOT/'comparison'/c/t['question']['question_id'],c,metrics) for t in tasks for c in CONDITIONS]
    summaries=[]
    for condition in CONDITIONS:
        rr=[r for r in rows if r['condition']==condition]
        count=lambda key:sum(bool(r.get(key,False)) for r in rr)
        total=lambda key:sum(r.get(key,0) for r in rr)
        ins=[r for r in rr if r['family']=='insufficient_support']
        s={'condition':condition,'denominator':24,'attempted':count('attempted'),
           'first_final_valid':count('first_attempt_valid'),'valid_after_repair':count('valid_after_repair'),
           'complete_visible':count('complete_requested_coverage'),'complete_method_selected':count('complete_method_selected_coverage'),
           'insufficient_cases_both_answered':sum(r['complete_requested_coverage'] and set(r['scoped_insufficiency_items'])=={'personal_change','course_comparison'} for r in ins),
           'missing_analysis_items':sum(len(r['missing_requested_analyses']) for r in rr),
           'retrieved_but_omitted_items':sum(len(r['retrieved_but_omitted']) for r in rr),
           'accepted_dashboard_omissions':sum(len(r['retrieved_but_omitted']) for r in rr if r['valid_after_repair']),
           'oracle_retrieved_upper_bound':count('oracle_retrieved_upper_bound'),
           'scoped_insufficiency_items':sum(len(r['scoped_insufficiency_items']) for r in rr),
           'error_episode_counts':dict(Counter(t for r in rr for t in r['error_categories'])),
           'selection_mismatch_episode_counts':dict(Counter(t for r in rr for t in r['selection_mismatch_categories'])),
           'unsupported_quantitative_attempts_rejected':sum(len(r['unsupported_quantitative_attempts_rejected']) for r in rr),
           'unsupported_accepted_quantitative_answers':sum(r['unsupported_accepted_quantitative_answers'] or 0 for r in rr),
           'compiler_supplied_answer_items':sum(len(r['compiler_supplied_answers']) for r in rr),
           'tool_calls':total('tool_calls_attempted'),'duplicate_exact_calls':total('redundant_requests'),
           'duplicate_equivalent_calls':total('redundant_equivalent_analyses'),'generations':total('generations'),
           'repairs':total('repairs'),'prompt_tokens':total('prompt_tokens'),'completion_tokens':total('completion_tokens'),
           'episode_seconds':total('elapsed_seconds'),'generation_seconds':total('generation_seconds'),
           'compiler_added_panels':total('compiler_added_panels'),'compiler_added_claims':total('compiler_added_claims'),
           'derived_metadata_records':total('derived_metadata_records'),'neutral_compiler_headings':count('neutral_compiler_heading'),
           'fallbacks':count('fallback'),'failed_questions':[r['question_id'] for r in rr if r['attempted'] and not r['valid_after_repair']],
           'unattempted_questions':[r['question_id'] for r in rr if not r['attempted']]}
        s['engineering_gate_met']=s['complete_visible']>=22 and s['unsupported_accepted_quantitative_answers']==0 and s['insufficient_cases_both_answered']==4
        summaries.append(s)
    pairs=[];paired=[]
    for label,left,right in [('complete_intervention','compact_a','binding_c'),('identity_ablation','derived_b','binding_c'),('metadata_package','compact_a','derived_b')]:
        group=[]
        for t in tasks:
            qid=t['question']['question_id'];a=next(r for r in rows if r['question_id']==qid and r['condition']==left);b=next(r for r in rows if r['question_id']==qid and r['condition']==right)
            group.append({'comparison':label,'left':left,'right':right,'question_id':qid,'family':a['family'],
                          'outcome':paired_outcome(a['complete_requested_coverage'],b['complete_requested_coverage']),
                          'selected_outcome':paired_outcome(a['complete_method_selected_coverage'],b['complete_method_selected_coverage']),
                          'left_complete':a['complete_requested_coverage'],'right_complete':b['complete_requested_coverage'],
                          'both_attempted':a['attempted'] and b['attempted']})
        pairs.extend(group);paired.append({'comparison':label,'left':left,'right':right,'denominator':24,
           'outcomes':dict(Counter(p['outcome'] for p in group)),'selected_outcomes':dict(Counter(p['selected_outcome'] for p in group)),
           'net_complete_gain':sum(p['right_complete']-p['left_complete'] for p in group)})
    events=[json.loads(s) for s in (ROOT/'model_ledger.jsonl').read_text().splitlines()]
    ends=[e for e in events if e['event']=='process_finished'];parts=dict(Counter(e['budget_partition'] for e in events if e['event']=='generation_started'))
    report={'created_utc':now(),'summaries':summaries,'paired_comparisons':paired,'generation_partitions':parts,
            'total_generations':sum(parts.values()),'model_process_seconds':sum(e['elapsed_seconds'] for e in ends),
            'model_processes':ends,'unclosed_processes':sorted({e['process_id'] for e in events if e['event']=='process_started'}-{e['process_id'] for e in ends}),
            'interpretation':'24 paired development people in known families; no prior-stage pooling, held-out/generalization or human-review claim.'}
    for name,value in [('per_case',rows),('paired_cases',pairs),('comparison',report)]:write_json(out/(name+'.json'),value)
    keys=['condition','question_id','family','status','attempted','first_attempt_valid','valid_after_repair','complete_requested_coverage','complete_method_selected_coverage','tool_calls_attempted','generations','repairs','prompt_tokens','completion_tokens','elapsed_seconds']
    with (out/'per_case.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=keys,extrasaction='ignore');w.writeheader();w.writerows(rows)
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()

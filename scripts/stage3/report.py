"""Frozen scoring/report path: keep every question and all attempted failures."""
import csv, json
from collections import Counter
from pathlib import Path
from trajectory_dashboards.common import read_json,write_json,now
from trajectory_dashboards.stage3.core import ROOT,METHODS,Engine
from trajectory_dashboards.stage3.evaluation import score_case
from trajectory_dashboards.stage2.integrity import validate


def main():
    out=ROOT/'reports';out.mkdir(parents=True,exist_ok=True)
    if (out/'per_question.json').exists():raise ValueError('Report exists; preserve version')
    tasks=read_json(ROOT/'tasks/manifest.json')['tasks'];engine=Engine();rows=[]
    metrics=[read_json(p) for p in (ROOT/'gpu/generations').glob('*.metadata.json')]
    for t in tasks:
        q=t['question']
        for method in ['baseline',*METHODS]:
            case=ROOT/'pilot'/method/q['question_id']
            r=score_case(q,case);r.update(method=method,case_id=t['case_id'],phrasing=t['phrasing'],family=q['kind'])
            if r['valid_after_permitted_repair']:
                a=case/'accepted';s,e=validate(engine,q,read_json(a/'spec.json'),read_json(a/'evidence.json'))
                r['selected_signatures']=sorted({(x.feature,x.reference,x.request.window) for x in e.values()})
                r['compiler_additions']={'controlled_wording_and_values':True,'standard_context':True,'inserted_analyses':0,'inserted_missing_claims':0}
                r['unsupported_accepted_quantitative_claims']=0
            else:r.update(selected_signatures=[],compiler_additions=None,unsupported_accepted_quantitative_claims=None)
            if (case/'request_state.json').exists():
                state=read_json(case/'request_state.json');r['request_map']=state['request_map'];r['stopping_status']=state['stopping_status']
                r['claimed_complete_but_incomplete']=state['stopping_status']=='complete' and not r['complete_requested_coverage']
            else:r.update(request_map=[],stopping_status='no model-authored state',claimed_complete_but_incomplete=False)
            mm=[m for m in metrics if m.get('budget_partition')=='pilot' and m['question_id']==q['question_id'] and m['method']==method]
            if method!='baseline':
                r['generations']=len(mm)
                r['prompt_tokens']=sum(m.get('prompt_tokens',0) for m in mm)
                r['completion_tokens']=sum(m.get('completion_tokens',0) for m in mm)
            r['generation_seconds']=sum(m['elapsed_seconds'] for m in mm)
            r['cuda_event_seconds']=sum(m.get('cuda_event_ms',0)/1000 for m in mm)
            requests=[]
            if (case/'requests.json').exists():requests=read_json(case/'requests.json')
            elif (case/'sequence.json').exists():
                requests=[t['request'] for s in read_json(case/'sequence.json') for t in s.get('tool_results',[])]
            profile=engine.registry.profile(q); sig=[]
            for req in requests:
                rule=engine.cfg['references'][req['reference']]
                win=profile[req.get('window','recent')];ref=profile['baseline'] if rule['time']=='baseline' else win
                sig.append((req['feature'],rule['group'],tuple(win),tuple(ref)))
            r['redundant_equivalent_analyses']=len(sig)-len(set(sig))
            rows.append(r)
    summaries=[];paired=[]
    for method in ['baseline',*METHODS]:
        rr=[r for r in rows if r['method']==method]
        pairs=[]
        for cid in sorted({t['case_id'] for t in tasks}):
            a,b=sorted([r for r in rr if r['case_id']==cid],key=lambda r:r['phrasing'])
            pattern=lambda r: [(c['id'],c['covered'],c['outcome']) for c in r['requested_answers']]
            pair={'case_id':cid,'method':method,'family':a['family'],'question_ids':[a['question_id'],b['question_id']],
                  'complete_a':a['complete_requested_coverage'],'complete_b':b['complete_requested_coverage'],
                  'complete_phrasings':int(a['complete_requested_coverage'])+int(b['complete_requested_coverage']),
                  'mean_answer_fraction':(a['answer_fraction']+b['answer_fraction'])/2,
                  'fraction_b_minus_a':b['answer_fraction']-a['answer_fraction'],
                  'completeness_agreement':a['complete_requested_coverage']==b['complete_requested_coverage'],
                  'answer_pattern_agreement':pattern(a)==pattern(b),
                  'validity_agreement':a['valid_after_permitted_repair']==b['valid_after_permitted_repair'],
                  'selected_analysis_agreement':a['selected_signatures']==b['selected_signatures']}
            pairs.append(pair);paired.append(pair)
        summaries.append({'method':method,'question_denominator':24,'case_denominator':12,
          'first_final_valid':sum(r.get('first_attempt_valid',False) for r in rr),
          'valid_after_repair':sum(r['valid_after_permitted_repair'] for r in rr),
          'complete_requested':sum(r['complete_requested_coverage'] for r in rr),
          'complete_method_selected':sum(r['complete_method_selected_coverage'] for r in rr),
          'complete_required_context':sum(r['complete_required_context'] for r in rr),
          'mean_requested_fraction':sum(r['answer_fraction'] for r in rr)/24,
          'cases_both_phrasings_complete':sum(p['complete_phrasings']==2 for p in pairs),
          'paired_completeness_agreement':sum(p['completeness_agreement'] for p in pairs),
          'paired_answer_pattern_agreement':sum(p['answer_pattern_agreement'] for p in pairs),
          'paired_selected_analysis_agreement':sum(p['selected_analysis_agreement'] for p in pairs),
          'failed_questions':[r['question_id'] for r in rr if not r['valid_after_permitted_repair']],
          'repairs':sum(r.get('repairs',0) for r in rr),'fallbacks':sum(r.get('fallback',False) for r in rr),
          'requested_analysis_missing':sum(len(r['missing_requested_analyses']) for r in rr),
          'retrieved_but_omitted':sum(len(r['retrieved_but_omitted']) for r in rr),
          'compiler_supplied_answer_count':sum(len(r['compiler_supplied_answers']) for r in rr),
          'claimed_complete_but_incomplete':sum(r['claimed_complete_but_incomplete'] for r in rr),
          'tool_calls':sum(r.get('tool_calls_attempted',0) for r in rr),
          'redundant_exact_requests':sum(r.get('redundant_requests',0) for r in rr),
          'redundant_equivalent_analyses':sum(r['redundant_equivalent_analyses'] for r in rr),
          'generations':sum(r.get('generations',0) for r in rr),
          'prompt_tokens':sum(r.get('prompt_tokens',0) for r in rr),'completion_tokens':sum(r.get('completion_tokens',0) for r in rr),
          'episode_seconds':sum(r.get('elapsed_seconds',0) for r in rr),
          'generation_seconds':sum(r['generation_seconds'] for r in rr),'cuda_event_seconds':sum(r['cuda_event_seconds'] for r in rr)})
    ledgers=[json.loads(s) for s in (ROOT/'model_ledger.jsonl').read_text().splitlines()]
    starts=[x for x in ledgers if x['event']=='process_started'];ends=[x for x in ledgers if x['event']=='process_finished']
    partitions=Counter(x.get('budget_partition','unknown') for x in ledgers if x['event']=='generation_started')
    write_json(out/'per_question.json',rows);write_json(out/'paired_cases.json',paired)
    write_json(out/'comparison.json',{'created_utc':now(),'methods':summaries,'model_processes':ends,'unclosed_processes':sorted({x['process_id'] for x in starts}-{x['process_id'] for x in ends}),'generation_partitions':dict(partitions),'total_attempted_generations':sum(partitions.values()),'model_process_seconds':sum(x['elapsed_seconds'] for x in ends),'timing_note':'CPU analyses and all inference on the same GPU host. Shared load/profile overhead lives in runtime.json, not assigned to policies. Pod billing time unknown.','interpretation':'One frozen development run, 12 case units with paired phrasings, not 24 independent people or stochastic repeatability; human scientific review outstanding.'})
    columns=['method','question_id','case_id','family','phrasing','status','first_attempt_valid','valid_after_permitted_repair','complete_requested_coverage','complete_method_selected_coverage','answer_fraction','tool_calls_attempted','generations','repairs','prompt_tokens','completion_tokens','elapsed_seconds']
    with open(out/'per_question.csv','w') as f:
        writer=csv.DictWriter(f,fieldnames=columns,extrasaction='ignore');writer.writeheader();writer.writerows(rows)
    lines=['# Frozen Stage 3 development pilot','', '| Method | First valid | Valid after repair | Complete requested | Method-selected complete | Both phrasings complete | Tools | Generations |', '|---|---:|---:|---:|---:|---:|---:|---:|']
    lines.extend(f"| {r['method']} | {r['first_final_valid']}/24 | {r['valid_after_repair']}/24 | {r['complete_requested']}/24 | {r['complete_method_selected']}/24 | {r['cases_both_phrasings_complete']}/12 | {r['tool_calls']} | {r['generations']} |" for r in summaries)
    lines.extend(['','All frozen questions and failures remain in the denominator. Paired phrasings are dependent. Integrity is source-bound and vocabulary constrained; zero unsupported accepted quantitative claims is not a guarantee about unrestricted text or human usefulness.','', 'Optional panels and compiler caveats are separately recorded; no panel-count bonus. See per_question.json for scoped answers/omissions and paired_cases.json for within-person phrasing changes.'])
    (out/'COMPARISON.md').write_text('\n'.join(lines)+'\n')
    print(summaries)

if __name__=='__main__':main()

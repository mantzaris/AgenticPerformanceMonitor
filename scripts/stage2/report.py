"""Keep every frozen task in the denominator, including failures and no output."""
import argparse,csv,json,statistics
from pathlib import Path
from trajectory_dashboards.common import read_json,write_json,now
from trajectory_dashboards.stage2.core import ROOT
from trajectory_dashboards.stage2.evaluation import score
from trajectory_dashboards.stage2.backend import Engine
from trajectory_dashboards.stage2.integrity import validate


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--subset',choices=['construction','pilot'],default='pilot');args=parser.parse_args()
    rubrics=[r for r in read_json(ROOT/'evaluator_only/rubrics.json')['rubrics'] if r['subset']==args.subset]
    engine=Engine();rows=[]
    metadata=[read_json(p) for p in (ROOT/'gpu/generations').glob('*.metadata.json')]
    for rubric in rubrics:
        for method in ('baseline','generic','reference_sensitive'):
            case=ROOT/args.subset/method/rubric['question_id']
            if (case/'result.json').exists():
                result=read_json(case/'result.json')
            else:
                # Construction deliberately runs only one policy per focal person.
                result={'method':method,'question_id':rubric['question_id'],'status':'not_attempted','first_attempt_valid':False,'repairs':0,'fallback':False,'tool_calls_attempted':0,'tool_calls_executed':0,'elapsed_seconds':0,'generations':0,'prompt_tokens':0,'completion_tokens':0,'reason':'construction allocation' if args.subset=='construction' else 'missing frozen pilot episode'}
            records=[m for m in metadata if m['question_id']==rubric['question_id'] and m['method']==method]
            if method!='baseline':
                result.update(generations=len(records),prompt_tokens=sum(m.get('prompt_tokens',0) for m in records),completion_tokens=sum(m.get('completion_tokens',0) for m in records),generation_seconds=sum(m.get('elapsed_seconds',0) for m in records),cuda_event_seconds=sum(m.get('cuda_event_ms',0) for m in records)/1000)
            if (case/'accepted/spec.json').exists():
                validate(engine,read_json(case/'accepted/question.json'),read_json(case/'accepted/spec.json'),read_json(case/'accepted/evidence.json'))
            rows.append(score(result,case,rubric))
    summary=[]
    for method in ('baseline','generic','reference_sensitive'):
        rr=[r for r in rows if r['method']==method]
        relevant=[r for r in rr if r['insufficient_expected']]
        summary.append({'method':method,'denominator':len(rr),'attempted':sum(r['status']!='not_attempted' for r in rr),'first_attempt_valid':sum(r['first_attempt_valid'] for r in rr),'valid_after_repair':sum(r['valid_after_permitted_repair'] for r in rr),'repaired':sum(r['status']=='agent_generated_and_repaired' for r in rr),'failed_or_not_attempted':sum(not r['valid_after_permitted_repair'] for r in rr),'all_task_context_covered':sum(r['all_task_context_covered'] for r in rr),'mean_coverage_fraction_all_tasks':statistics.mean(r['coverage_fraction'] for r in rr),'insufficiency_tasks':len(relevant),'appropriate_insufficiency':sum(bool(r['appropriate_insufficiency']) for r in relevant),'unsupported_claims_in_accepted_output':sum(r['unsupported_claims_in_accepted_output'] or 0 for r in rr),'tool_calls_attempted':sum(r.get('tool_calls_attempted',0) for r in rr),'tool_calls_executed':sum(r.get('tool_calls_executed',0) for r in rr),'generations':sum(r['generations'] for r in rr),'prompt_tokens':sum(r['prompt_tokens'] for r in rr),'completion_tokens':sum(r['completion_tokens'] for r in rr),'episode_seconds':sum(r['elapsed_seconds'] for r in rr),'generation_seconds':sum(r.get('generation_seconds',0) for r in rr),'cuda_event_seconds':sum(r.get('cuda_event_seconds',0) for r in rr),'adaptive_episodes':sum(r.get('subsequent_analysis_after_results',False) for r in rr),'fallbacks':sum(r.get('fallback',False) for r in rr)})
    out=ROOT/'reports';out.mkdir(exist_ok=True)
    write_json(out/f'{args.subset}_per_task.json',rows)
    ledgers=[json.loads(s) for s in (ROOT/'model_ledger.jsonl').read_text().splitlines()]
    process=[e for e in ledgers if e['event']=='process_finished']
    write_json(out/f'{args.subset}_comparison.json',{'created_utc':now(),'subset':args.subset,'methods':summary,'gpu_process_runtime':process,'total_gpu_process_seconds':sum(e['elapsed_seconds'] for e in process),'total_attempted_generations':sum(e['event']=='generation_started' for e in ledgers),'interpretation':'Single-run engineering pilot on development people; no statistical superiority/generalization/repeatability inference. Rubric awaits external human review. Compiler context is not agent-selected investigation.','allocation_note':'Model loading and other shared process overhead is reported per process, not arbitrarily allocated to policies. Per-policy generation/CUDA-event/episode time is shown separately; none is RunPod billing time.'})
    columns=['task_id','method','status','first_attempt_valid','valid_after_permitted_repair','coverage_fraction','all_task_context_covered','appropriate_insufficiency','tool_calls_attempted','generations','prompt_tokens','completion_tokens','elapsed_seconds','error']
    with open(out/f'{args.subset}_per_task.csv','w') as f:
        writer=csv.DictWriter(f,fieldnames=columns,extrasaction='ignore');writer.writeheader();writer.writerows(rows)
    md=['# '+args.subset.capitalize()+' comparison','', '| Method | First valid | Valid after repair | Full context | Mean coverage | Appropriate insufficiency | Tools | Generations |', '|---|---:|---:|---:|---:|---:|---:|---:|']
    for s in summary:
        md.append(f"| {s['method']} | {s['first_attempt_valid']}/{s['denominator']} | {s['valid_after_repair']}/{s['denominator']} | {s['all_task_context_covered']}/{s['denominator']} | {s['mean_coverage_fraction_all_tasks']:.3f} | {s['appropriate_insufficiency']}/{s['insufficiency_tasks']} | {s['tool_calls_attempted']} | {s['generations']} |")
    md+=['','All tasks remain in the denominator. A separately available baseline is not agent success. See per-task JSON for omissions, validity failures, compiler context and cost. Automatic rubrics await external review.']
    (out/f'{args.subset}_comparison.md').write_text('\n'.join(md)+'\n')
    print('\n'.join(md))

if __name__=='__main__':main()

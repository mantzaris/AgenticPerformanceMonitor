"""The strong unchanged enumeration method, timed on the GPU host's CPU."""
import platform, subprocess, time
from trajectory_dashboards.common import read_json,write_json,now,commit
from trajectory_dashboards.stage2.methods import deterministic
from trajectory_dashboards.stage3.core import ROOT,Engine,event
from trajectory_dashboards.stage3.display import render


def main():
    # Same frozen inputs as every agent. Machine identity is recorded, not network details.
    from gpu_pilot import verify_freeze
    frozen=verify_freeze()
    gpu=subprocess.check_output(['nvidia-smi','--query-gpu=name','--format=csv,noheader'],text=True).strip()
    if 'RTX 6000 Ada' not in gpu:raise ValueError('Baseline timing must run on the intended GPU host CPU')
    engine=Engine()
    for task in read_json(ROOT/'tasks/manifest.json')['tasks']:
        q=task['question'];case=ROOT/'pilot/baseline'/q['question_id']
        if (case/'started.json').exists() or (case/'result.json').exists():continue
        case.mkdir(parents=True,exist_ok=True)
        write_json(case/'started.json',{'utc':now(),'execution_commit':commit(),'freeze_sha256':frozen})
        start=time.monotonic()
        result={'method':'baseline','question_id':q['question_id'],'status':'failed','first_attempt_valid':False,'repairs':0,'generations':0,'prompt_tokens':0,'completion_tokens':0,'fallback':False,'redundant_requests':0,'host_gpu':gpu,'analysis_device':'CPU','cpu_architecture':platform.machine(),'execution_commit':commit()}
        try:
            spec,evidence,requests=deterministic(engine,q)
            write_json(case/'tool_results.json',{eid:e.model_dump() for eid,e in evidence.items()})
            write_json(case/'requests.json',[r.model_dump() for r in requests])
            render(engine,q,spec,evidence,case/'accepted',origin='deterministic enumeration baseline')
            result.update(status='deterministic_accepted',first_attempt_valid=True,tool_calls_attempted=len(requests),tool_calls_executed=len(requests))
        except Exception as exc:
            result['error']=f'{type(exc).__name__}: {exc}'
        result.update(elapsed_seconds=time.monotonic()-start,completed_utc=now())
        write_json(case/'result.json',result);event({'event':'baseline_episode_finished',**result})
        print(result,flush=True)

if __name__=='__main__':main()

import argparse,time
from pathlib import Path
from trajectory_dashboards.common import read_json,write_json,now,commit,digest
from trajectory_dashboards.stage2.core import ROOT,append_event
from trajectory_dashboards.stage2.backend import Engine
from trajectory_dashboards.stage2.methods import deterministic
from trajectory_dashboards.stage2.display import render


def main():
    p=argparse.ArgumentParser();p.add_argument('--subset',choices=['construction','pilot'],required=True);a=p.parse_args()
    engine=Engine()
    for task in read_json(ROOT/'tasks/manifest.json')['tasks']:
        if task['subset']!=a.subset:continue
        q=task['question'];case=ROOT/a.subset/'baseline'/q['question_id']
        if (case/'result.json').exists():raise ValueError('Episode exists; do not rerun')
        start=time.monotonic()
        result={'method':'baseline','question_id':q['question_id'],'started_utc':now(),'execution_commit':commit(),'config_sha256':digest(engine.cfg),'generations':0,'prompt_tokens':0,'completion_tokens':0,'repairs':0,'fallback':False,'status':'failed','first_attempt_valid':False}
        try:
            spec,evidence,requests=deterministic(engine,q)
            write_json(case/'tool_calls.json',[r.model_dump() for r in requests])
            write_json(case/'tool_results.json',{k:e.model_dump() for k,e in evidence.items()})
            result['tool_calls_attempted']=result['tool_calls_executed']=len(requests)
            render(engine,q,spec,evidence,case/'accepted',origin='deterministic baseline')
            result.update(status='deterministic_accepted',first_attempt_valid=True)
        except Exception as exc:result['error']=f'{type(exc).__name__}: {exc}'
        result.update(elapsed_seconds=time.monotonic()-start,completed_utc=now())
        write_json(case/'result.json',result);append_event({'event':'baseline_episode_finished','subset':a.subset,**result})
        print(result,flush=True)

if __name__=='__main__':main()

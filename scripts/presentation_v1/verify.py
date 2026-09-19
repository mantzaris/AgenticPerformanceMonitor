"""Verify immutability and replay selected results with the old numerical validator."""
import argparse
from pathlib import Path
from trajectory_dashboards.common import read_json, write_json, file_hash
from trajectory_dashboards.presentation_v1.model import EXAMPLES


def history():
    inv=read_json('artifacts/presentation_v1/historical_inventory.json')
    changed=[p for p,sha in inv['files'].items() if not Path(p).is_file() or file_hash(p)!=sha]
    if changed:
        raise AssertionError('Historical file changes: '+str(changed))
    return {'status':'PASS','starting_commit':inv['starting_commit'],'unchanged_files':len(inv['files'])}


def verify(output, replay=False):
    result={'history':history(),'new_inference_generations':0,'cases':[]}
    if replay:
        from trajectory_dashboards.stage6.core import Engine
        from trajectory_dashboards.stage2.integrity import validate
        from trajectory_dashboards.stage6.adapter import replay as historical_replay
        import tempfile
        engine=Engine()
        for slug,label,method,case in EXAMPLES:
            source=Path(f'artifacts/stage6/comparison/{method}/{case}/accepted')
            spec,evidence=validate(engine,read_json(source/'question.json'),read_json(source/'spec.json'),read_json(source/'evidence.json'))
            with tempfile.TemporaryDirectory(prefix='apm-presentation-replay-') as tmp:
                historical_replay(engine,source,tmp)
                for filename in ['spec.json','evidence.json','selection_provenance.json']:
                    assert read_json(Path(tmp)/filename)==read_json(source/filename),filename
            result['cases'].append({'case':case,'method':method,'source_bound_numerical_validation':'PASS','historical_replay':'PASS','records':len(evidence)})
    write_json(output,result)
    print(result)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',default='artifacts/presentation_v1/verification.json');p.add_argument('--replay',action='store_true');args=p.parse_args()
    verify(args.output,args.replay)

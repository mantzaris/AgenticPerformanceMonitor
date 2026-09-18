from pathlib import Path
from trajectory_dashboards.common import write_json,read_json,file_hash,commit,now,digest
from trajectory_dashboards.stage4.core import ROOT,FullAction,event
from trajectory_dashboards.stage4.semantic import SemanticAction


def main():
    target=ROOT/'protocol/freeze.json'
    if target.exists():raise ValueError('Freeze exists; never replace it')
    if (ROOT/'pilot').exists():raise ValueError('Freeze must precede every pilot method')
    write_json(ROOT/'protocol/full_schema.json',FullAction.model_json_schema())
    write_json(ROOT/'protocol/semantic_schema.json',SemanticAction.model_json_schema())
    paths=[]
    for directory,pattern in [('src/trajectory_dashboards','*.py'),('scripts/stage4','*.py'),('tests','*.py'),('docs/stage4','*.md'),('artifacts/stage4/source','*'),('artifacts/stage4/tasks','*.json'),('artifacts/stage4/evaluator_only','*.json')]:
        paths.extend(p for p in Path(directory).rglob(pattern) if p.is_file() and '__pycache__' not in str(p))
    paths.extend(Path(p) for p in ['configs/stage1.json','configs/stage2.json','configs/stage3.json','configs/stage3_prompts.json','configs/stage4.json','configs/stage4_prompts.json','artifacts/data/splits.json','artifacts/gpu/model_manifest.json','artifacts/stage4/protocol/execution_order.json','artifacts/stage4/protocol/interface_differences.json','artifacts/stage4/protocol/full_schema.json','artifacts/stage4/protocol/semantic_schema.json','pyproject.toml','requirements.lock'])
    value={'version':'stage4-v1','frozen_utc':now(),'source_commit':commit(),'files':{str(p):file_hash(p) for p in sorted(set(paths))},'protocol_deviations':[],'rule':'No tuning or successful-case reruns after this freeze; future protocol deviations must be separate artifacts.'}
    write_json(target,value);event({'event':'pilot_frozen','freeze_sha256':digest(value),'files':len(paths),'source_commit':commit()})
    print(digest(value))

if __name__=='__main__':main()

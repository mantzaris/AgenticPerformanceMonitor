"""Freeze scientific/pilot inputs once. Later reporting must not rewrite them."""
from pathlib import Path
from trajectory_dashboards.common import write_json,file_hash,commit,now,digest
from trajectory_dashboards.stage2.core import ROOT,append_event

def main():
    target=ROOT/'protocol/freeze.json'
    if target.exists():raise ValueError('Freeze already exists; do not replace it')
    if (ROOT/'pilot').exists() and any((ROOT/'pilot').rglob('started.json')):
        raise ValueError('Pilot inference already started')
    files=[]
    for directory,pattern in [('src/trajectory_dashboards','*.py'),('scripts/stage2','*.py'),('tests','*.py'),('docs/stage2','*.md'),('artifacts/stage2/source','*'),('artifacts/stage2/tasks','*.json'),('artifacts/stage2/evaluator_only','*.json')]:
        files.extend(p for p in Path(directory).rglob(pattern) if p.is_file() and '__pycache__' not in str(p))
    files.extend(Path(p) for p in ['configs/stage1.json','configs/stage2.json','configs/stage2_prompts.json','artifacts/data/splits.json','artifacts/gpu/model_manifest.json','artifacts/stage2/protocol/schemas.json','pyproject.toml','requirements.lock'])
    frozen={'version':'stage2-pilot-v1','frozen_utc':now(),'source_commit':commit(),'pilot_started':False,'files':{str(p):file_hash(p) for p in sorted(set(files))},'rule':'No tuning on pilot results. Any change to listed inputs is an explicitly reported deviation. Reporting/inspection artifacts are outside this hash set.'}
    write_json(target,frozen)
    append_event({'event':'pilot_frozen','source_commit':commit(),'freeze_sha256':digest(frozen),'files':len(frozen['files'])})
    print('Frozen',len(frozen['files']),'files:',digest(frozen))

if __name__=='__main__':main()

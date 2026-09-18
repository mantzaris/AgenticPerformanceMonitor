"""Freeze source, question selection, hidden evaluation, interfaces and execution."""
from pathlib import Path
from trajectory_dashboards.common import read_json,write_json,file_hash,digest,commit,now
from trajectory_dashboards.stage4.semantic import SemanticAction
from trajectory_dashboards.stage6.binding import DerivedAction,BindingAction
from trajectory_dashboards.stage6.core import ROOT,event


def main():
    target=ROOT/'protocol/freeze.json'
    if target.exists() or (ROOT/'comparison').exists():raise ValueError('Freeze once, before comparison')
    assert read_json(ROOT/'checks/prefreeze_verification.json')['status']=='PASS'
    for name,cls in [('compact_a',SemanticAction),('derived_b',DerivedAction),('binding_c',BindingAction)]:
        write_json(ROOT/'protocol'/(name+'_schema.json'),cls.model_json_schema())
    assert read_json(ROOT/'protocol/compact_a_schema.json')==read_json('artifacts/stage5/protocol/semantic_schema.json')
    files=[]
    for directory,pattern in [('src','*.py'),('scripts/stage6','*.py'),('configs','*.json'),('docs/stage4','*.md'),('docs/stage6','*.md'),
                              ('artifacts/stage6/source','*'),('artifacts/stage6/tasks','*.json'),('artifacts/stage6/evaluator_only','*.json'),('artifacts/stage6/protocol','*.json')]:
        files.extend(p for p in Path(directory).rglob(pattern) if p.is_file() and '__pycache__' not in p.parts)
    files.extend(Path(p) for p in ['artifacts/data/splits.json','artifacts/stage5/models/qwen14b/manifest.json',
        'artifacts/stage5/checks/capacity_qwen14b.json','artifacts/stage5/protocol/semantic_schema.json',
        'tests/test_stage6.py','pyproject.toml','requirements.lock'])
    value={'version':'stage6-v1','frozen_utc':now(),'source_commit':commit(),'files':{str(p):file_hash(p) for p in sorted(set(files))},
           'protocol_deviations':[],'rule':'No tuning/reruns, source/score/prompt/interface edits after comparison freeze'}
    write_json(target,value);event({'event':'comparison_frozen','freeze_sha256':digest(value),'files':len(files),'source_commit':commit()});print(digest(value))


if __name__=='__main__':main()

"""Freeze all scientific inputs and execution/reporting code before comparison."""
from pathlib import Path
from trajectory_dashboards.common import write_json, read_json, file_hash, commit, now, digest
from trajectory_dashboards.stage4.core import FullAction
from trajectory_dashboards.stage4.semantic import SemanticAction
from trajectory_dashboards.stage5.core import ROOT, event


def main():
    target = ROOT / 'protocol/freeze.json'
    if target.exists() or (ROOT / 'comparison').exists():
        raise ValueError('Freeze must be unique and precede every comparison method')
    for model in ['qwen7b', 'qwen14b']:
        assert read_json(ROOT / f'checks/capacity_{model}.json')['status'] == 'PASS'
    write_json(ROOT / 'protocol/full_schema.json', FullAction.model_json_schema())
    write_json(ROOT / 'protocol/semantic_schema.json', SemanticAction.model_json_schema())
    for name in ['full_schema.json', 'semantic_schema.json']:
        assert read_json(ROOT / 'protocol' / name) == read_json(Path('artifacts/stage4/protocol') / name)
    paths = []
    for directory, pattern in [('src', '*.py'), ('scripts/stage5', '*.py'), ('docs/stage4', '*.md'),
                               ('docs/stage5', '*.md'), ('artifacts/stage5/source', '*'),
                               ('artifacts/stage5/tasks', '*.json'), ('artifacts/stage5/evaluator_only', '*.json'),
                               ('artifacts/stage5/models', '*')]:
        paths.extend(p for p in Path(directory).rglob(pattern) if p.is_file() and '__pycache__' not in p.parts
                     and p.suffix not in {'.jsonl', '.txt'})
    paths.extend(Path(p) for p in [
        'configs/stage1.json', 'configs/stage2.json', 'configs/stage3.json', 'configs/stage3_prompts.json',
        'configs/stage4.json', 'configs/stage4_prompts.json', 'configs/stage5.json',
        'artifacts/data/splits.json', 'artifacts/gpu/model_manifest.json',
        'artifacts/stage5/protocol/execution_order.json', 'artifacts/stage5/protocol/full_schema.json',
        'artifacts/stage5/protocol/semantic_schema.json', 'artifacts/stage5/checks/capacity_qwen7b.json',
        'artifacts/stage5/checks/capacity_qwen14b.json', 'tests/test_stage5.py',
        'artifacts/stage4/gpu/generations/026_s4_build_s3_01_semantic_format_check.input.json',
        'pyproject.toml', 'requirements.lock'])
    value = {'version': 'stage5-v1', 'frozen_utc': now(), 'source_commit': commit(),
             'files': {str(p): file_hash(p) for p in sorted(set(paths))}, 'protocol_deviations': [],
             'rule': 'No prompt/interface/statistical/scoring changes or successful-case reruns after freeze.'}
    write_json(target, value)
    event({'event': 'comparison_frozen', 'freeze_sha256': digest(value), 'files': len(value['files']), 'source_commit': commit()})
    print(digest(value))


if __name__ == '__main__':
    main()

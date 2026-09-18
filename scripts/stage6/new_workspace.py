"""Create an isolated reproduction workspace without replacing saved artifacts."""
import argparse
import shutil
from pathlib import Path
from trajectory_dashboards.common import read_json, write_json, commit


def main():
    p = argparse.ArgumentParser()
    p.add_argument('destination')
    p.add_argument('--prepare', action='store_true')
    args = p.parse_args()
    out = Path(args.destination).resolve()
    if out.exists():
        raise ValueError('Choose a fresh destination')
    if args.prepare:
        files = []
        for directory in ['src', 'scripts/stage6', 'configs', 'docs/stage4', 'docs/stage6', 'artifacts/stage5/source']:
            files.extend(p for p in Path(directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
        files.extend(Path(p) for p in ['pyproject.toml', 'requirements.lock', 'artifacts/data/splits.json', 'artifacts/stage5/tasks/manifest.json'])
    else:
        freeze = Path('artifacts/stage6/protocol/freeze.json')
        files = [Path(p) for p in read_json(freeze)['files']] + [freeze]
    for source in files:
        target = out / source
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    write_json(out / 'source_revision.json', {'commit': commit(), 'reproduction_workspace': True})
    print(out)


if __name__ == '__main__':
    main()

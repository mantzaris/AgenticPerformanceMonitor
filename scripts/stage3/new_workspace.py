"""Copy immutable inputs to a new workspace; never erase historical attempts."""
import argparse, shutil
from pathlib import Path
from trajectory_dashboards.common import read_json,write_json,commit


def main():
    p=argparse.ArgumentParser();p.add_argument('destination');p.add_argument('--prepare',action='store_true');args=p.parse_args()
    out=Path(args.destination).resolve()
    if out.exists():raise ValueError('Choose a nonexistent destination')
    out.mkdir(parents=True)
    if args.prepare:
        files=[]
        for directory in ['src','scripts/stage3','configs','docs/stage3','tests','artifacts/stage2/source']:
            files.extend(x for x in Path(directory).rglob('*') if x.is_file() and '__pycache__' not in str(x))
        files.extend(Path(x) for x in ['pyproject.toml','requirements.lock','artifacts/data/splits.json','artifacts/data/questions.json','artifacts/stage2/tasks/manifest.json'])
    else:
        freeze=Path('artifacts/stage3/protocol/freeze.json')
        files=[Path(x) for x in read_json(freeze)['files']]+[freeze]
    for source in files:
        target=out/source;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
    write_json(out/'source_revision.json',{'commit':commit(),'reproduction_workspace':True})
    print(out)

if __name__=='__main__':main()

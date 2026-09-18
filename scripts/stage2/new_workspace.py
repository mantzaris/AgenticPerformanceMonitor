"""Copy frozen inputs to a fresh independent reproduction workspace, never erase results."""
import argparse,shutil
from pathlib import Path
from trajectory_dashboards.common import read_json,write_json,file_hash,commit

def main():
    p=argparse.ArgumentParser();p.add_argument('directory');args=p.parse_args()
    destination=Path(args.directory)
    if destination.exists():raise ValueError('Choose a new directory; existing work is never overwritten')
    freeze=read_json('artifacts/stage2/protocol/freeze.json')
    files=list(freeze['files'])+['artifacts/stage2/protocol/freeze.json']
    for name in files:
        source=Path(name)
        if name in freeze['files'] and file_hash(source)!=freeze['files'][name]:raise ValueError('Frozen input mismatch: '+name)
        target=destination/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
    write_json(destination/'source_revision.json',{'commit':commit(),'purpose':'Fresh optional reproduction from frozen Stage 2 inputs; historical outputs/ledgers retained in original repository'})
    print(destination.resolve())

if __name__=='__main__':main()

"""CPU/browser-only end-to-end regeneration. Run from the repository root."""
import argparse,subprocess
from pathlib import Path

def main(output,chromium,inspect):
 root=Path(output).resolve()
 if not root.name.startswith('predraft_v1'):raise ValueError('Use a separate predraft_v1 output namespace')
 root.mkdir(parents=True,exist_ok=True);(root/'checks').mkdir(exist_ok=True)
 commands=[['.venv/bin/python','scripts/predraft_v1/build.py'],['.venv/bin/python','scripts/predraft_v1/review_packet.py'],['python3','scripts/predraft_v1/vector_figures.py'],['.venv/bin/python','scripts/predraft_v1/capture.py','--chromium',chromium],['python3','scripts/predraft_v1/compose.py'],['python3','scripts/predraft_v1/proof.py'],['python3','scripts/predraft_v1/verify.py']]
 if inspect:commands.append(['.venv/bin/python','scripts/predraft_v1/browser_review.py','--chromium',chromium])
 for cmd in commands:subprocess.run(cmd+['--output',str(root)],check=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',default='artifacts/predraft_v1');p.add_argument('--chromium',default='/snap/bin/chromium');p.add_argument('--inspect',action='store_true');a=p.parse_args();main(a.output,a.chromium,a.inspect)

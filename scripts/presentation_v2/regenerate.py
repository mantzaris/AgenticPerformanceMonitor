"""One CPU-only command; original artifacts and manuscript are never overwritten."""
import argparse
import subprocess
from pathlib import Path

if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--output', default='artifacts/presentation_v2')
    p.add_argument('--chromium', default='/snap/bin/chromium'); p.add_argument('--inspect', action='store_true')
    args = p.parse_args(); dest = Path(args.output).resolve()
    # Explicitly prevent accidentally choosing any historical output root.
    historical = ['artifacts/presentation_v1','artifacts/predraft_v1','artifacts/stage6','paper']
    assert dest != Path.cwd() and not any(dest == Path(h).resolve() or Path(h).resolve() in dest.parents for h in historical)
    for cmd in [
        ['.venv/bin/python', 'scripts/presentation_v2/build.py', '--output', str(dest)],
        ['.venv/bin/python', 'scripts/presentation_v2/capture.py', '--output', str(dest), '--chromium', args.chromium],
        ['python3', 'scripts/presentation_v2/compose.py', '--output', str(dest)],
        ['python3', 'scripts/presentation_v2/proof.py', '--output', str(dest)],
    ]:
        subprocess.run(cmd, check=True)
    if args.inspect:
        subprocess.run(['.venv/bin/python', 'scripts/presentation_v2/browser_review.py', '--output', str(dest), '--chromium', args.chromium], check=True)

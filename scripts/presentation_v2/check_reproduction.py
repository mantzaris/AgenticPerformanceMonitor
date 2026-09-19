"""Compare a fresh render tree to the delivered export bytes."""
import argparse
import hashlib
import json
from pathlib import Path

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--output', default='artifacts/presentation_v2')
    ap.add_argument('--replica', default='artifacts/presentation_v2/reproduction_build'); args = ap.parse_args()
    root, replica = Path(args.output), Path(args.replica)
    files = [*root.glob('captures/*.png'), *root.glob('figures/*.pdf'), *root.glob('figures/*.png'),
             *root.glob('gallery/*/charts/*.svg'), *root.glob('proof/page_*.png'), root/'proof/layout.pdf']
    rows = [{'file': str(p.relative_to(root)), 'original_sha256': sha(p),
             'rebuilt_sha256': sha(replica/p.relative_to(root))} for p in sorted(files)]
    differences = [r['file'] for r in rows if r['original_sha256'] != r['rebuilt_sha256']]
    record = {'compared_files': len(rows), 'byte_identical': len(rows)-len(differences),
              'differences': differences, 'records': rows,
              'method': 'Fresh build, real browser capture, composition and template proof in a separate directory. Native charts, all individual PNGs, composite PDFs/PNGs and proof pages compared; manifests/HTML contain destination-specific links and are not byte-compared.'}
    (root/'checks/reproduction.json').write_text(json.dumps(record, indent=2)+'\n')
    print(len(rows)-len(differences), '/', len(rows), 'exports byte-identical; differences:', differences)
    assert not differences

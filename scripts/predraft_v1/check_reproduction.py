"""Compare final artifacts to a separately regenerated output tree."""
import argparse,hashlib,json
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main(original,replica):
 a=Path(original);b=Path(replica)
 paths=sorted({p.relative_to(a) for pattern in ['captures/*.png','figures/*.pdf','figures/*.png','figures/*.svg','gallery/*/charts/*.svg','proof/layout.pdf','proof/page_*.png','human_review/reviewer*.csv','human_review/reviewer*.json','human_review/adjudication.*','results_categories.*'] for p in a.glob(pattern)})
 changed=[str(p) for p in paths if not (b/p).exists() or sha(a/p)!=sha(b/p)]
 report={'original':str(a),'regenerated':str(b),'artifacts_compared':len(paths),'byte_identical':len(paths)-len(changed),'differences':changed,'scope':'All captures, figure PDFs/PNGs/SVGs, chart SVGs, compiled layout PDF and proof pages, frozen-count derivatives and blank forms. Path-bearing HTML/manifests may differ by output root.','status':'PASS' if not changed else 'FAIL'}
 (a/'checks/reproduction.json').write_text(json.dumps(report,indent=2)+'\n');print(report);assert not changed
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--original',default='artifacts/predraft_v1');p.add_argument('--replica',default='artifacts/predraft_v1_reproduction');a=p.parse_args();main(a.original,a.replica)

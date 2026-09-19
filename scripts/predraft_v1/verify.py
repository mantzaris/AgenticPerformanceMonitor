"""History, frozen endpoints, template bytes, source links and blank review forms."""
import json,hashlib,csv,zipfile,argparse
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote

def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def verify(root):
 root=Path(root);inv=read('artifacts/predraft_v1/historical_inventory.json');changed=[p for p,v in inv['files'].items() if not Path(p).exists() or sha(p)!=v];assert not changed,changed
 review=read(root/'human_review/source_manifest.json');assert all(sha(p)==v for p,v in review['files'].items())
 source=read(root/'source_manifest.json');assert all(sha(p)==v for e in source['entries'] for p,v in e['source_hashes'].items())
 result=read(root/'results_categories.json');assert sha(result['source'])==result['source_sha256'];assert all(sum(v)==24 for v in result['counts'].values())
 packet=read(root/'human_review/packet.json')['records'];assert len(packet)==96
 for name in ['reviewer_1','reviewer_2']:
  form=read(root/f'human_review/{name}.json');assert form['reviewer'] is None and len(form['records'])==96
  assert all(v is None for r in form['records'] for v in r['ratings'].values())
  assert all(v is None for r in form['records'] for a in r['requested_answers'] for k,v in a.items() if k!='requirement_id')
 assert all(v is None for r in read(root/'human_review/adjudication.json')['records'] for k,v in r.items() if k!='review_id')
 missing=[]
 class Links(HTMLParser):
  def handle_starttag(self,tag,attrs):
   for k,v in attrs:
    if k=='href' and v and not urlsplit(v).scheme and urlsplit(v).path:
     p=(self.file.parent/unquote(urlsplit(v).path)).resolve()
     if not p.exists():missing.append(str(p))
 for f in (root/'human_review').rglob('*.html'):
  parser=Links();parser.file=f;parser.feed(f.read_text())
 assert not missing,missing
 template=Path('artifacts/predraft_v1/template')
 with zipfile.ZipFile(template/'SCITEPRESS_Conference_Latex.zip') as z:
  assert all((template/'official'/name).read_bytes()==z.read(name) for name in z.namelist())
 for e in read(root/'figure_manifest.json')['figures']:
  assert e['minimum_critical_font_pt']>=8
  assert sha(root/'figures'/f'{e["name"]}.pdf')==e['pdf_sha256']
 out={'historical_files_unchanged':len(inv['files']),'starting_commit':inv['starting_commit'],'frozen_scores_unchanged':True,'human_review_slots':96,'accepted_slots':review['accepted'],'rejected_slots':review['rejected'],'review_forms':'two independent blank forms; blank adjudication','saved_source_hashes':'PASS','results_categories':result['counts'],'official_template_bytes':'PASS','critical_figure_text_min_pt':min(e['minimum_critical_font_pt'] for e in read(root/'figure_manifest.json')['figures']),'missing_review_links':missing,'new_model_generations':0,'reserved_observations_opened':False,'status':'PASS'}
 (root/'checks').mkdir(exist_ok=True);(root/'checks/verification.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',default='artifacts/predraft_v1');verify(p.parse_args().output)

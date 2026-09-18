"""Loopback-only form server: a reference/window change executes a new pipeline."""
import argparse,json,mimetypes,uuid
from http.server import BaseHTTPRequestHandler,HTTPServer
from pathlib import Path
from urllib.parse import parse_qs,unquote,urlparse
from ..common import read_json,write_json,file_hash,digest,now
from .core import ROOT,Question,Request,event
from .core import Engine
from ..stage2.integrity import validate
from ..stage2.methods import specification
from .display import render


def followup(engine,parent,reference,profile,output_root=None):
    parent=Path(parent).resolve()
    root=ROOT.resolve()
    if not parent.is_relative_to(root) or not (parent/'spec.json').is_file():
        raise ValueError('Parent must be a saved Stage 3 dashboard within artifacts/stage3')
    if reference not in engine.cfg['references'] or profile not in engine.cfg['profiles']:
        raise ValueError('Reference/window profile is outside the admissible registry')
    original=read_json(parent/'question.json')
    # Verify the saved parent before using its analytical identity.
    parent_spec,parent_evidence=validate(engine,original,read_json(parent/'spec.json'),read_json(parent/'evidence.json'))
    feature=parent_evidence[parent_spec.evidence_ids[0]].feature
    parent_hashes={n:file_hash(parent/n) for n in ('question.json','spec.json','evidence.json','bound.json')}
    p=engine.cfg['profiles'][profile]
    child_id=original['question_id']+'_followup_'+uuid.uuid4().hex[:10]
    q=Question.model_validate({**original,'question_id':child_id,'profile':profile,'cutoff_day':p['cutoff_day'],'text':f"Follow-up: use {reference} with earlier weeks {p['baseline'][0]}–{p['baseline'][1]}, recent weeks {p['recent'][0]}–{p['recent'][1]}, and information through day {p['cutoff_day']}."})
    request=Request(question_id=child_id,feature=feature,reference=reference,window='recent')
    # Fresh deterministic dispatch, not relabeling/cosmetic selection of old evidence.
    e=engine.analyze(q,request)
    spec=specification(q,[e])
    link={'parent_question_id':original['question_id'],'parent_path':str(parent.relative_to(Path.cwd())),'parent_hashes':parent_hashes,'requested_reference':reference,'requested_profile':profile,'executed_utc':now(),'request':request.model_dump(),'new_evidence_id':e.evidence_id,'new_source_bundle_sha256':e.provenance['source_bundle_sha256']}
    output_root=Path(output_root or ROOT/'followups')
    child=output_root/child_id
    render(engine,q,spec,{e.evidence_id:e},child,origin='deterministic follow-up requested by local user',parent=link)
    write_json(child/'link.json',link)
    assert parent_hashes=={n:file_hash(parent/n) for n in parent_hashes}
    if child.resolve().is_relative_to(ROOT.resolve()):
        event({'event':'followup_executed','parent_question_id':original['question_id'],'child_question_id':child_id,'reference':reference,'profile':profile,'child_path':str(child),'status':e.status})
    return child


def handler(engine):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,format,*args):pass
        def do_GET(self):
            path=Path(unquote(urlparse(self.path).path).lstrip('/')).resolve()
            if not path.is_relative_to(ROOT.resolve()) or not path.is_file():
                self.send_error(404,'Choose a saved Stage 3 dashboard path');return
            content=path.read_bytes();self.send_response(200)
            self.send_header('Content-Type',mimetypes.guess_type(path)[0] or 'application/octet-stream')
            self.send_header('Content-Length',str(len(content)));self.end_headers();self.wfile.write(content)
        def do_POST(self):
            if self.path!='/followup':self.send_error(404);return
            try:
                length=int(self.headers.get('Content-Length','0'))
                if not 0<length<=8192:raise ValueError('Invalid form size')
                fields=parse_qs(self.rfile.read(length).decode(),strict_parsing=True)
                if set(fields)!={'parent','reference','profile'} or any(len(v)!=1 for v in fields.values()):raise ValueError('Expected parent, reference and profile once each')
                child=followup(engine,fields['parent'][0],fields['reference'][0],fields['profile'][0])
                self.send_response(303);self.send_header('Location','/'+str(child/'dashboard.html'));self.end_headers()
            except Exception as exc:
                self.send_error(400,str(exc))
    return Handler


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8766);args=parser.parse_args()
    server=HTTPServer(('127.0.0.1',args.port),handler(Engine()))
    print(f'Local Stage 3 follow-up server on http://127.0.0.1:{args.port}; open a saved artifacts/stage3/.../dashboard.html path.',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()

if __name__=='__main__':main()

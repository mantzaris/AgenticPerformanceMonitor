"""Verify the archived official template without altering any supplied file."""
import hashlib,json,re,zipfile
from pathlib import Path
ROOT=Path('artifacts/predraft_v1/template')
def main():
    archive=ROOT/'SCITEPRESS_Conference_Latex.zip'
    with zipfile.ZipFile(archive) as z:
        for name in z.namelist():
            target=ROOT/'official'/name
            assert target.read_bytes()==z.read(name),name
    sty=(ROOT/'official/SCITEPRESS.sty').read_text()
    assert r'\setlength\textwidth{6.221in}' in sty
    assert r'\setlength\columnsep{0.8cm}' in sty
    result={'source_page':'https://icaart.scitevents.org/Templates.aspx','source_archive':'https://www.scitepress.org/documents/SCITEPRESS_Conference_Latex.zip','retrieved_utc':'2026-09-19','retrieval':'curl HTTPS; original archive and every extracted byte retained','archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'textwidth_inches':6.221,'textwidth_mm':6.221*25.4,'columnsep_mm':8,'columnwidth_mm':(6.221*25.4-8)/2,'geometry_unmodified':True,'official_files':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'official').iterdir())}}
    (ROOT/'manifest.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
if __name__=='__main__':main()

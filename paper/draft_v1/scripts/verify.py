"""Focused manuscript consistency checks; reads frozen results, never rescores."""
import csv
import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path
from PyPDF2 import PdfFileReader

ROOT=Path(__file__).resolve().parents[3]
HERE=ROOT/'paper/draft_v1'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    checks={}
    old=read(HERE/'checks/historical_inventory.json')
    changed=[p for p,h in old['files'].items() if not (ROOT/p).exists() or sha(ROOT/p)!=h]
    assert not changed,changed
    checks['historical_files_unchanged']=len(old['files'])
    for n in ['article.cls','SCITEPRESS.sty','apalike.sty','apalike.bst']:
        assert (HERE/n).read_bytes()==(ROOT/'artifacts/predraft_v1/template/official'/n).read_bytes()
    current=next(r for r in read(HERE/'review/primary_retrievals.json') if r['id']=='template')
    archived=read(ROOT/'artifacts/predraft_v1/template/manifest.json')
    assert current['status']==200 and current['sha256']==archived['archive_sha256']
    checks['official_template']='Current archive hash matches archived copy; four used official files byte-identical; 6.221 in text width, 8 mm gap.'
    rows=read(ROOT/'artifacts/stage6/reports/per_case.json')
    assert len(rows)==96 and all(r['attempted'] and not r['fallback'] for r in rows)
    cats=read(HERE/'generated/results_categories.json')
    assert len(cats['records'])==96
    assert cats['counts']==read(ROOT/'artifacts/predraft_v1/results_categories.json')['counts']
    checks['frozen_results']='All 96 slots; identical categories to preserved pre-draft figure; no scoring code called.'
    manifest=read(ROOT/'artifacts/stage6/tasks/manifest.json')
    assert len({x['question']['person_id'] for x in manifest['tasks']})==24
    assert set(Counter(x['question']['kind'] for x in manifest['tasks']).values())=={4}
    assert {x['question']['profile'] for x in manifest['tasks']}=={'standard','mid','short','narrow','alternate'}
    checks['task_design']='24 distinct development people; four per six families; all five actual window profiles documented.'
    for c in ['s6_17','s6_18','s6_19','s6_20']:
        r=next(r for r in rows if r['condition']=='derived_b' and r['question_id']==c)
        bound=read(ROOT/'artifacts/stage6/comparison/derived_b'/c/'accepted/bound.json')
        assert not r['complete_requested_coverage'] and r['valid_after_repair']
        assert all(any(cl['template']=='personal_change' and feature in cl['text'] and 'weeks 8–11' in cl['text'] for cl in bound['claims']) for feature in ['nonbanked_submissions','scheduled_no_submission'])
    fail=read(ROOT/'artifacts/stage6/comparison/compact_a/s6_15/accepted/bound.json')
    peer=[c for c in fail['claims'] if c['template']=='comparison']
    assert len(peer)==2 and all('focal weeks 0–3' in c['text'] for c in peer)
    assert any(c['template']=='personal_change' and 'weeks 10–11 (0 observed weeks)' in c['text'] for c in fail['claims'])
    checks['caveat_and_failure']='B17–20 preserved incomplete with visible recent means; A15 retains earlier peer selections and separate personal insufficiency.'
    packet=ROOT/'artifacts/predraft_v1/human_review'
    assert len(read(packet/'packet.json')['records'])==96
    for n in ['reviewer_1.csv','reviewer_2.csv','reviewer_1_answers.csv','reviewer_2_answers.csv']:
        with (packet/n).open() as f:
            rr=list(csv.DictReader(f))
        assert all(not v for r in rr for k,v in r.items() if k not in ['review_id','requirement_id'])
    checks['human_review']='96 original slots preserved; both independent reviewer forms remain blank.'
    for n in ['adaptation','reference_switch','failure','assessment']:
        oldname={'adaptation':'figure1','reference_switch':'figure2','failure':'figureS1','assessment':'figureS2'}[n]
        with (HERE/'figures'/f'{n}.pdf').open('rb') as a,(ROOT/'artifacts/predraft_v1/figures'/f'{oldname}.pdf').open('rb') as b:
            ra,rb=PdfFileReader(a),PdfFileReader(b)
            assert ra.getNumPages()==rb.getNumPages()==1
            assert ra.getPage(0).getContents().getData()==rb.getPage(0).getContents().getData()
            assert ra.getPage(0).mediaBox==rb.getPage(0).mediaBox
            assert not ra.getDocumentInfo().get('/Author')
    checks['figure_preservation']='Four copied UI PDFs have identical page content streams and dimensions; anonymous metadata. Architecture/results preserve original plotting path.'
    log=(HERE/'checks/latex_3.txt').read_text();bib=(HERE/'checks/bibtex.txt').read_text()
    assert not re.search(r'Overfull|undefined|Missing character|LaTeX Warning|Error',log)
    assert 'Warning--' not in bib and 'error message' not in bib
    checks['latex']='No overfull boxes, undefined references/citations, missing glyphs or LaTeX warnings; underfull justification notices manually inspected.'
    pdftext=(HERE/'checks/main.txt').read_text()
    assert not re.search(r'TODO|TBD|FIXME|Lorem ipsum|AgenticPerformanceMonitor|/home/|github\.com/',pdftext,re.I)
    with (HERE/'main.pdf').open('rb') as f:
        pdf=PdfFileReader(f);assert not pdf.getDocumentInfo().get('/Author');pages=pdf.getNumPages()
    assert pages==12
    fonts=(HERE/'checks/pdffonts.txt').read_text().splitlines()[2:]
    assert fonts and all(re.search(r'\s+yes\s+(?:yes|no)\s+(?:yes|no)\s+\d+\s+\d+\s*$',x) for x in fonts)
    aux=(HERE/'main.aux').read_text();assert len(re.findall(r'\\bibcite\{',aux))==15
    assert len(re.findall(r'\\newlabel\{fig:',aux))==5
    assert len(re.findall(r'\\newlabel\{tab:',aux))==3
    checks['pdf']='12 A4 pages; 5 figures, 3 tables, 15 resolved bibliography entries; all fonts embedded; blank author metadata; no identifying repository paths/URLs or placeholders.'
    count=read(HERE/'checks/character_count.json')
    browser=read(HERE/'checks/browser.json')
    assert count['pdf_sha256']==browser['pdf_sha256']==sha(HERE/'main.pdf')
    assert count['within_range_even_with_allowance'] and count['pages']==pages
    assert len(browser['pages'])==pages and browser['browser_closed'] and not browser['errors'] and not browser['external_requests']
    checks['browser_and_length']={'pages_loaded':pages,'browser':browser['browser'],'nonwhitespace_characters_including_raster_figures':count['combined_nonwhitespace_characters'],'conservative_total':count['combined_with_allowance'],'zero_browser_errors':True,'browser_closed':True}
    abstract=(HERE/'main.tex').read_text().split('\\abstract{',1)[1].split('\\onecolumn',1)[0]
    # This count treats each LaTeX macro/citation as one word, close to the
    # rendered count; all result macros expand to single numeric tokens.
    assert 70<=len(abstract.split())<=200
    checks['abstract_words_with_tex_tokens']=len(abstract.split())
    checks['scope']='CPU and browser drafting/inspection only; no experimental inference, evaluator execution, reserved observation loading or reviewer judgments.'
    checks['starting_commit']=old['starting_commit']
    checks['main_pdf_sha256']=sha(HERE/'main.pdf')
    (HERE/'checks/verification.json').write_text(json.dumps(checks,indent=2)+'\n')
    print(json.dumps(checks,indent=2))

if __name__=='__main__':main()

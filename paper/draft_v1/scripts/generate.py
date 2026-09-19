"""Read frozen reports; generate publication tables/copies without rescoring."""
import hashlib
import importlib.util
import json
import shutil
from pathlib import Path
from PyPDF2 import PdfFileReader, PdfFileWriter

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'paper/draft_v1'
REPORT = ROOT / 'artifacts/stage6/reports'
ORDER = ['baseline', 'compact_a', 'derived_b', 'binding_c']
LABEL = dict(zip(ORDER, ['Enumeration', 'A: compact', 'B: derived metadata', 'C: explicit binding']))

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    import os
    os.chdir(ROOT)
    report = json.loads((REPORT / 'comparison.json').read_text())
    rows = json.loads((REPORT / 'per_case.json').read_text())
    detail = json.loads((REPORT / 'resource_detail.json').read_text())
    summaries = {s['condition']: s for s in report['summaries']}
    assert len(rows) == 96 and len({(r['condition'], r['question_id']) for r in rows}) == 96
    categories = {}
    for m in ORDER:
        rr = [r for r in rows if r['condition'] == m]
        assert len(rr) == 24 and all(r['attempted'] and not r['fallback'] for r in rr)
        valid = sum(r['valid_after_repair'] for r in rr)
        visible = sum(r['valid_after_repair'] and r['complete_requested_coverage'] for r in rr)
        selected = sum(r['valid_after_repair'] and r['complete_method_selected_coverage'] for r in rr)
        first = sum(r['first_attempt_valid'] for r in rr)
        assert (valid, visible, selected, first) == tuple(summaries[m][k] for k in ['valid_after_repair','complete_visible','complete_method_selected','first_final_valid'])
        categories[m] = [selected, visible-selected, valid-visible, 24-valid]
        assert all(x >= 0 for x in categories[m]) and sum(categories[m]) == 24
    expected = [[24,0,0,0],[18,3,1,2],[14,1,9,0],[11,4,6,3]]
    assert list(categories.values()) == expected  # checks, never plotted inputs
    gen = OUT / 'generated'
    def table(name, header, body, fmt):
        (gen / name).write_text('%% Generated from frozen reports; do not edit.\n\\begin{tabular}{'+fmt+'}\n\\hline\n'+header+' \\\\\n\\hline\n'+'\n'.join(' & '.join(map(str,r))+' \\\\' for r in body)+'\n\\hline\n\\end{tabular}\n')
    table('outcomes.tex', 'Condition & First valid & Accepted & Visible complete & Selected complete & Both insuff. answers',
          [[LABEL[m]] + [str(summaries[m][k])+'/24' for k in ['first_final_valid','valid_after_repair','complete_visible','complete_method_selected']] + [str(summaries[m]['insufficient_cases_both_answered'])+'/4'] for m in ORDER], 'lrrrrr')
    table('costs.tex', 'Condition & Tools & Repeated$^{a}$ & Generations & Input / output tokens & Episode s & Median s',
          [[LABEL[m], summaries[m]['tool_calls'], str(summaries[m]['duplicate_exact_calls'])+' / '+str(summaries[m]['duplicate_equivalent_calls']),summaries[m]['generations'],f"{summaries[m]['prompt_tokens']:,} / {summaries[m]['completion_tokens']:,}",f"{summaries[m]['episode_seconds']:.2f}",f"{detail['conditions'][m]['median_episode_seconds']:.2f}"] for m in ORDER], 'lrrrrrr')
    shorts = dict(zip(ORDER,['Enum','A','B','C']))
    table('paired.tex','Right $-$ left & Both & Right only & Left only & Neither',
          [[shorts[p['right']]+' $-$ '+shorts[p['left']]] + [p['outcomes'][k] for k in ['both_complete','right_only_complete','left_only_complete','both_incomplete']] for p in report['paired_comparisons']], 'lrrrr')
    macros=[]
    for m in ORDER:
        for name,key in [('Visible','complete_visible'),('Selected','complete_method_selected'),('Accepted','valid_after_repair')]:
            macros.append('\\newcommand{\\'+shorts[m]+name+'}{'+str(summaries[m][key])+'}')
    (gen/'numbers.tex').write_text('\n'.join(macros)+'\n')
    # Reuse the earlier numerical plotting path with only publication labeling
    # and metadata changed. No scoring function is imported or executed.
    spec=importlib.util.spec_from_file_location('historical_vectors',ROOT/'scripts/predraft_v1/vector_figures.py')
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    def save(fig, root, name):
        for text in fig.texts:
            if text.get_text() == 'Stage 6 · frozen development results':
                text.set_text('Frozen development comparison')
        label={'figure3':'architecture','figure4':'results'}[name]
        fig.savefig(OUT/'figures'/f'{label}.pdf',metadata={'CreationDate':None,'ModDate':None,'Creator':'Publication figure builder','Author':''})
        fig.savefig(OUT/'figures'/f'{label}.svg',metadata={'Date':None,'Creator':'Publication figure builder'})
        fig.savefig(OUT/'figures'/f'{label}.png',dpi=300)
        mod.plt.close(fig)
    mod.save=save
    mod.counts(gen);mod.architecture(gen)
    figures=[]
    for src,name in [('figure1','adaptation'),('figure2','reference_switch'),('figureS1','failure'),('figureS2','assessment')]:
        p=ROOT/'artifacts/predraft_v1/figures'/f'{src}.pdf'
        writer=PdfFileWriter()
        with p.open('rb') as f:
            reader=PdfFileReader(f)
            for page in reader.pages:writer.addPage(page)
            writer.addMetadata({'/Title':name.replace('_',' ').title(),'/Author':'','/Creator':'Publication copy; unchanged page content'})
            with (OUT/'figures'/f'{name}.pdf').open('wb') as g:writer.write(g)
        figures.append({'publication':f'figures/{name}.pdf','source':str(p.relative_to(ROOT)),'source_sha256':sha(p),'publication_sha256':sha(OUT/'figures'/f'{name}.pdf'),'change':'PDF metadata only; page content unchanged; raster browser panels plus vector editorial labels'})
    official=ROOT/'artifacts/predraft_v1/template/official'
    for name in ['article.cls','SCITEPRESS.sty','apalike.sty','apalike.bst']:
        shutil.copyfile(official/name,OUT/name)
    sources=[REPORT/'comparison.json',REPORT/'per_case.json',REPORT/'resource_detail.json',ROOT/'scripts/predraft_v1/vector_figures.py',ROOT/'artifacts/predraft_v1/capture_manifest.json',ROOT/'artifacts/predraft_v1/figure_manifest.json']
    (gen/'provenance.json').write_text(json.dumps({'sources':{str(p.relative_to(ROOT)):sha(p) for p in sources},'categories':categories,'figures':figures,'vector_figures':'Architecture and results regenerated by original vector functions; results title loses internal Stage 6 label; anonymous metadata. Same geometry, values and caveat.','template':{n:sha(OUT/n) for n in ['article.cls','SCITEPRESS.sty','apalike.sty','apalike.bst']}},indent=2)+'\n')
    print('96 frozen slots verified; tables and six publication figures generated.')

if __name__ == '__main__':main()

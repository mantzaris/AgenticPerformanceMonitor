"""Reuse the preserved mapper/charts, adding presentation-only structure and state."""
from pathlib import Path

from ..predraft_v1.render import render as inherited_render
from ..presentation_v1.render import h, comparison_card
from ..presentation_v1.model import reference_name
from ..presentation_v1.render import window
from ..common import write_json, file_hash


def render(model, output):
    """Layouts still dispatch on selected claims and support, never case IDs."""
    out = Path(output)
    entry = inherited_render(model, out)
    css = Path(__file__).with_name('style.css').read_text()
    script = Path(__file__).with_name('interaction.js').read_text()
    status = {'agent original': 'Saved agent output',
              'agent repaired': 'Saved agent output · historically repaired'}.get(
                  model['selection_status'], 'Saved enumeration output')
    responsibility = '''<details class="responsibility"><summary>Who supplied this view?</summary>
<dl><dt>Agent / enumeration</dt><dd>Selected analytical answers and evidence.</dd>
<dt>Analytical tools</dt><dd>Calculated all values, counts and peer-mean intervals.</dd>
<dt>Original compiler</dt><dd>Supplied the tagged context, wording and required panels.</dd>
<dt>Presentation v2</dt><dd>Organizes saved content, draws charts and changes emphasis. No new analysis or repair.</dd></dl>
<p>Numerical binding does not establish that the question is fully answered.</p></details>'''
    reference_note = '''<p class="reference-definition">Presentation peers are other development students in the same course offering. The saved pool excludes the focal person and all task focal people. Exact definitions remain in the evidence inspector.</p>'''
    for route in ['index.html', 'figure.html']:
        page = (out / route).read_text()
        # Replace only inherited interaction code; saved-state JSON is untouched.
        start = page.rindex('<script>')
        end = page.index('</script>', start) + len('</script>')
        page = page[:start] + '<script>' + script + '</script>' + page[end:]
        page = page.replace('</style>', css + '</style>', 1)
        page = page.replace('<body>', '<body class="presentation-v2 wide-view">', 1)
        page = page.replace('<body class="preparation">', '<body class="preparation presentation-v2">', 1)
        page = page.replace('<nav class="site-nav">', '<a class="skip-link" href="#saved-answer">Skip to saved answer</a><nav class="site-nav">', 1)
        page = page.replace('<article class="figure-surface"', '<article id="saved-answer" class="figure-surface"', 1)
        page = page.replace('<div class="below-surface">', responsibility + reference_note + '<div class="below-surface">', 1)
        page = page.replace('Pre-draft excerpt.', 'Presentation v2 · selected-content excerpt.')
        # Historical repair status is visible, with no new completeness badge.
        marker = '<footer' if route == 'figure.html' else '<footer class="surface-footer"'
        pos = page.index(marker)
        page = page[:pos] + f'<p class="source-status">{h(status)} · new rendering</p>' + page[pos:]
        if model['layout'] == 'references' and model['switchable']:
            token = '</select>'
            controls = '''<p id="reference-warning" role="alert" hidden></p><a class="saved-permalink" id="saved-permalink" href="?">Link to this saved reference</a>'''
            page = page.replace(token, token + controls, 1)
        # The complete original question is still present in its expander.
        if route == 'index.html':
            page = page.replace('Compact reading view →', 'Publication excerpt →')
            page = page.replace(' weeks</span>', ' person-weeks</span>')
            # Short control names stay legible on phones. Exact definitions and
            # both windows remain visible in the synchronized card and chart.
            if model['layout'] == 'references' and model['switchable']:
                short_names = {'course': 'Presentation peers', 'early_stage': 'Earlier-period peers',
                               'same_prior_attempt': 'Same prior-attempt peers'}
                for eid in model['comparison_ids']:
                    e = model['evidence'][eid]
                    old = f'<option value="{eid}">{h(reference_name(e))} · {window(e["reference_window"])}</option>'
                    page = page.replace(old, f'<option value="{eid}">{short_names[e["reference"]]}</option>')
            if model['layout'] == 'personal':
                peers = [c for c in model['claims'] if c['template'] == 'comparison']
                by_recent = sorted(peers, key=lambda c: tuple(model['evidence'][c['evidence_id']]['window']), reverse=True)
                page = page.replace(''.join(comparison_card(c, model) for c in peers),
                                    ''.join(comparison_card(c, model) for c in by_recent), 1)
            page = page.replace('Recent minus earlier; no interval was estimated for this change.',
                                'Recent minus earlier. Differences are calculated before rounding. Uncertainty for the change was not estimated.')
        else:
            page = page.replace('Compact reading view →', 'Expanded reading view →').replace('href="figure.html">Expanded reading view', 'href="index.html">Expanded reading view')
        (out / route).write_text(page)
    # Do not replace the inherited source manifest or experimental provenance.
    manifest = {
        'schema': 'presentation-v2', 'source_hashes': model['source_hashes'],
        'layout': model['layout'], 'anonymous_label': model['label'],
        'historical_selection_status': model['selection_status'],
        'selected_answer_evidence': [{
            'template': c['template'], 'evidence_ids': c['evidence_ids'],
            'original_indices': c['original_indices'], 'origin': c['origin']
        } for c in model['claims']],
        'original_panels': model['panels'],
        'changes': ['responsive visual hierarchy', 'recent selected peer card first in personal view', 'visible historical selection status',
                    'responsibility expander', 'saved-reference URL state',
                    'inherited template-sized excerpts and native vector charts'],
        'statistical_recomputation': False, 'answer_completeness_evaluated': False,
        'new_substantive_answers': False,
        'rendered_files': {n: file_hash(out / n) for n in ['index.html', 'figure.html']},
    }
    write_json(out / 'presentation_v2.json', manifest)
    return {**entry, 'v2_manifest': str(out / 'presentation_v2.json'),
            'source_status': model['selection_status']}

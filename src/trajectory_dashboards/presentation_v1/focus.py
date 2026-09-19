"""Compact browser view for figure captures; full saved content remains below it.

These are explicitly excerpts. Emphasis follows selected analytical semantics,
never a case identifier or a completeness rubric.
"""
from .render import h, window, evidence_link, origin_label, save_chart
from .charts import num, trajectory, references, observation, assessment
from .model import FEATURES, reference_name
import re


def paper_chart(svg):
    return re.sub(r'font-size="(\d+)"', lambda match:f'font-size="{float(match[1])*1.15:.2f}"', svg)


def short_peer(c, m):
    e=m['evidence'][c['evidence_id']];s=e['summary']
    if e['status']!='supported':
        detail=f'Comparison unavailable · {s["focal_observations"]} observed focal weeks; {e["people"]:,} peers / {e["observations"]:,} person-weeks.'
    else:
        detail=f'Person {num(s["focal_mean"])} · peer {num(s["peer_mean"])} · difference {num(s["contrast"],True)}.'
    support=f'{e["people"]:,} peers / {e["observations"]:,} person-weeks. Peer mean 95% CI [{num(s["peer_ci_low"])}, {num(s["peer_ci_high"])}].' if e['status']=='supported' else ''
    return f'<div class="short-peer" data-evidence="{e["evidence_id"]}" data-answer="peer"><b>{h(reference_name(e))} · person {window(e["window"])}</b><p>{detail}</p><span>Reference {window(e["reference_window"])} · {h(e["unit"])}</span><p>{support}</p></div>'


def focused(m, out):
    evidence=m['evidence'];claims=m['claims'];panels=m['panels'];layout=m['layout']
    own=[c for c in claims if c['template']=='personal_change'];peers=[c for c in claims if c['template']=='comparison']
    first=next(iter(evidence.values()));s=first['summary'];state={};extra=''
    if layout in {'personal','support'}:
        e=evidence[own[0]['evidence_id']];s=e['summary']
        if s['personal_status']=='supported':
            main=f'<div class="focus-answer" data-answer="personal" data-evidence="{e["evidence_id"]}"><span>Personal change · {h(e["unit"])}</span><div class="focus-values"><b>{num(s["baseline_mean"])}</b><span>→</span><b>{num(s["recent_mean"])}</b><strong>{num(s["personal_change"],True)}</strong></div><p>Earlier → recent · {s["baseline_observations"]} / {s["recent_observations"]} observed weeks. No change interval.</p></div>'
        else:
            main=f'<div class="focus-answer" data-answer="personal" data-evidence="{e["evidence_id"]}"><strong>Personal comparison unavailable</strong><p>Earlier {window(s["baseline_window"])}: {s["baseline_observations"]} observed weeks.<br>Recent {window(s["recent_window"])}: {s["recent_observations"]} observed weeks.</p></div>'
        p=next(p for p in panels if p['kind']=='trajectory')
        main+=save_chart(out,'focus-trajectory',paper_chart(trajectory(evidence[p['evidence_id']])))
        # Emphasize recent comparisons only when actually selected. If none was
        # selected (the failure example), retain the selected earlier comparisons.
        recent=[c for c in peers if evidence[c['evidence_id']]['window']==s['recent_window']]
        chosen=recent or peers
        main+=''.join(short_peer(c,m) for c in chosen)
        if len(chosen)<len(peers):
            extra='Additional selected earlier peer comparison is available below.'
        note='Clicks are not effort or learning. Shading: 95% peer-mean CI; no interval for the person or change.'
    elif layout=='references' and m['switchable']:
        records=[evidence[c['evidence_id']] for c in peers]
        options=''.join(f'<option value="{e["evidence_id"]}">{h(reference_name(e))} · {window(e["reference_window"])}</option>' for e in records)
        for c in peers:
            e=evidence[c['evidence_id']];eid=e['evidence_id'];ss=e['summary'];chart=paper_chart(references(records,eid))
            save_chart(out,'focus-reference-'+eid,chart)
            card=f'<section class="focus-answer answer-card" data-answer="peer" data-evidence="{eid}"><b>{h(reference_name(e))}</b><p>Person <b>{num(ss["focal_mean"])}</b> · peer <b>{num(ss["peer_mean"])}</b> · Δ <b>{num(ss["contrast"],True)}</b></p><p>Person {window(e["window"])}; reference {window(e["reference_window"])}.</p><p>{e["people"]:,} peers / {e["observations"]:,} person-weeks.<br>Peer mean 95% CI [{num(ss["peer_ci_low"])}, {num(ss["peer_ci_high"])}].</p>{evidence_link(eid)}</section>'
            state[eid]={'card':card,'svg':chart,'reference':e['reference'],'window':e['window'],'reference_window':e['reference_window'],'evidence_href':f'#evidence-{eid}','summary':ss}
        initial=records[0]['evidence_id']
        main=f'<div class="focus-control"><label for="reference-select">View saved analysis</label><select id="reference-select">{options}</select></div><div id="reference-chart" class="chart">{state[initial]["svg"]}</div><div id="reference-result" aria-live="polite">{state[initial]["card"]}</div>'
        note='Same focal mean and scale throughout. Prior-attempt peers change the population; earlier peers change the reference period. CIs describe peer means only.'
        extra='All three selected contrasts and sample sizes are available below. No new investigation.'
    elif layout=='observations':
        p=next(p for p in panels if p['kind']=='observation_status');e=evidence[p['evidence_id']]
        main=f'<div class="focus-answer"><strong>{e["summary"]["focal_observations"]} observed weeks in the recent window</strong><p>Selected peer comparisons have insufficient support.</p></div><p class="focus-provenance">Original compiler context: observation timeline</p>'+save_chart(out,'focus-observations',paper_chart(observation(e)))
        main+='<div class="focus-missing">'
        for c in peers:
            e=evidence[c['evidence_id']]
            main+=f'<div data-answer="peer" data-evidence="{e["evidence_id"]}"><b>{h(e["unit"].capitalize())}</b><span>{num(e["summary"]["focal_mean"])}</span></div>'
        main+=f'</div><p class="focus-counts">Presentation peers: {first["people"]:,} people / {first["observations"]:,} person-weeks, {window(first["reference_window"])}.</p>'
        note='Unavailable is not zero. Eligibility is administrative; logging completeness is unknown. No inference about effort or learning. Grade limits are original compiler context: release times are unknown.'
        extra='Observation timeline and grade caveat: original compiler context. Dated assessment states are available below.'
    elif layout=='assessments':
        main='<div class="focus-assessment">'
        for c in peers:
            e=evidence[c['evidence_id']];ss=e['summary']
            main+=f'<div data-answer="peer" data-evidence="{e["evidence_id"]}"><b>{h(FEATURES[e["feature"]])}</b><strong>{num(ss["focal_mean"])}</strong><span>per observed week · {window(e["window"])}</span><p>Peer {num(ss["peer_mean"])} · difference {num(ss["contrast"],True)}.<br>Peer mean 95% CI [{num(ss["peer_ci_low"])}, {num(ss["peer_ci_high"])}].</p></div>'
        main+='</div>'
        p=next(p for p in panels if p['kind']=='assessment_status')
        main+=save_chart(out,'focus-assessments',paper_chart(assessment(evidence[p['evidence_id']])))
        main+=f'<p class="focus-counts">{first["summary"]["focal_observations"]} observed focal weeks · {first["people"]:,} peers / {first["observations"]:,} person-weeks.<br>Reference: presentation peers, {window(first["reference_window"])}.</p>'
        note='Marks and banking approval are unavailable; release times are unknown. Records do not establish learning, effort or failure. Due-date states are dated snapshots, not grades. CIs describe peer means only.'
        extra='Submission trajectory and click-record eligibility context are available below.'
    else:
        main=''.join(short_peer(c,m) for c in peers);note='Descriptive saved results only.'
    heading=m['question_heading']
    q=m['question']
    selector='Baseline' if m['method'].startswith('Deterministic') else 'Agent'
    surface=f'''<article class="figure-surface focus-surface" data-layout="{layout}" data-case="{h(m['label'])}"><header><div class="eyebrow">{h(m['label'])} · saved development case</div><h1>{h(heading)}</h1><p>Earlier {window(s['baseline_window'])} · recent {window(s['recent_window'])}<br>Course {h(q['course'].replace('_',' · '))} · through day {q['cutoff_day']}</p></header><div class="focus-main">{main}</div><aside class="focus-limit">{h(note)}</aside><footer><b>{h(m['method'])}</b><p>{selector} selections · deterministic numbers<br>New compact presentation · excerpt</p></footer></article><p class="excerpt-note">{h(extra)} <a href="index.html">Open expanded dashboard</a>. All original claims, panels, conclusion and provenance remain below; numerical validity does not establish completeness.</p>'''
    return surface,state

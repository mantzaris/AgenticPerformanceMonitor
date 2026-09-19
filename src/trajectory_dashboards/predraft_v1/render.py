"""Template-sized excerpts; v1 expanded content retained verbatim below/alongside."""
from pathlib import Path
import json,os
from ..presentation_v1.render import h,window,evidence_link,render as expanded_render
from ..presentation_v1.model import FEATURES,reference_name
from ..presentation_v1.charts import num
from . import charts

CSS='''
body.preparation{background:#f3f6f7;color:#192e38;font:20px/1.35 "DejaVu Sans",sans-serif;margin:0}
.preparation main{max-width:1000px;margin:auto;padding:16px 24px}.preparation .site-nav{font-size:18px}
.preparation .figure-surface{box-sizing:border-box;width:500px;max-width:100%;margin:auto;border:1px solid #dbe3e5;border-radius:6px;background:white;overflow:hidden}
.preparation .figure-surface *{box-sizing:border-box}.preparation .figure-surface header{padding:14px;border-bottom:1px solid #dbe3e5}
.preparation .figure-surface h1{font-size:25px;line-height:1.2;margin:6px 0 10px;font-weight:700}
.preparation .figure-surface p{font-size:20px;margin:8px 0}.preparation .eyebrow{font-size:20px;color:#176b72;font-weight:700}
.preparation .excerpt-content{padding:12px 14px}.preparation .answer{border:1px solid #cbdfe0;background:#f0f7f6;padding:10px;margin:0 0 12px}
.preparation .answer strong{font-size:25px}.preparation .mean-row{display:flex;gap:12px;align-items:baseline;margin:6px 0}.preparation .mean-row strong:last-child{margin-left:auto;color:#176b72}
.preparation .peer{border-top:1px solid #dbe3e5;padding:10px 0}.preparation .peer b{font-size:20px}
.preparation .chart svg{display:block;width:100%;height:auto}.preparation .chart{margin:8px 0}.preparation .note{background:#f5f7f8;border-left:3px solid #839ba4;padding:10px 12px;margin:0 14px 12px;font-size:20px}
.preparation .figure-surface footer{border-top:1px solid #dbe3e5;padding:10px 14px;font-size:20px;color:#506775}
.preparation label{display:block;font-weight:600;margin-bottom:6px}.preparation select{font:20px/1.3 "DejaVu Sans",sans-serif;width:100%;padding:8px 4px;background:white;color:#192e38;border:1px solid #8ea8b4;border-radius:3px}
.preparation .switch-excerpt{padding:14px}.preparation .switch-excerpt .answer{margin-bottom:0}.preparation .switch-excerpt .answer strong{font-size:24px}
.preparation .unavailable-item{display:flex;justify-content:space-between;gap:12px;padding:9px 0;border-top:1px solid #dbe3e5;font-size:20px}
.preparation .unavailable-item span:last-child{font-weight:700;color:#805722}.preparation a{color:#176b72}.preparation .figure-surface .evidence-link{font-size:20px}.preparation .provenance-label{color:#506775;font-size:20px;margin:8px 0}
.preparation .below-surface{font-size:17px}*{animation:none!important;transition:none!important;scroll-behavior:auto!important}
'''

def save(out,name,content):
    p=out/'charts'/f'predraft-{name}.svg';p.write_text(content)
    return f'<div class="chart">{content}</div>'

def peer(c,m,short=False):
    e=m['evidence'][c['evidence_id']];s=e['summary'];eid=e['evidence_id']
    body=f'<b>{h(reference_name(e))}</b><p>Person {window(e["window"])};<br>reference {window(e["reference_window"])}.</p>'
    if e['status']=='supported':
        body+=f'<p>Person {num(s["focal_mean"])} · peer {num(s["peer_mean"])}<br>Difference <b>{num(s["contrast"],True)}</b> {h(e["unit"])}</p><p>Peer mean 95% CI [{num(s["peer_ci_low"])}, {num(s["peer_ci_high"])}].</p>'
    else:body+=f'<p><b>Peer comparison unavailable</b><br>{s["focal_observations"]} observed focal weeks.<br>{h(e["unit"])}</p>'
    body+=f'<p>{e["people"]:,} peers / {e["observations"]:,} person-weeks.</p>'
    if short:
        body=f'<b>{h(reference_name(e))}</b><p>Person {window(e["window"])}; reference {window(e["reference_window"])}.</p>'
        if e['status']=='supported':
            body+=f'<p>Person {num(s["focal_mean"])} · peer {num(s["peer_mean"])} · Δ {num(s["contrast"],True)}.<br>Peer mean 95% CI [{num(s["peer_ci_low"])}, {num(s["peer_ci_high"])}].</p>'
        else:body+=f'<p><b>Peer comparison unavailable</b><br>{s["focal_observations"]} observed focal weeks.</p>'
        body+=f'<p>{e["people"]:,} peers / {e["observations"]:,} person-weeks.</p>'
    return f'<section class="peer" data-answer="peer" data-evidence="{eid}">{body}</section>'

def personal(c,m):
    e=m['evidence'][c['evidence_id']];s=e['summary']
    if s['personal_status']=='supported':
        content=f'<b>Personal change</b><div class="mean-row"><strong>{num(s["baseline_mean"])}</strong><span>→</span><strong>{num(s["recent_mean"])}</strong><strong>{num(s["personal_change"],True)}</strong></div><p>{h(e["unit"])}<br>{s["baseline_observations"]} earlier / {s["recent_observations"]} recent observed weeks.</p><p>Difference calculated before rounding.</p>'
    else:content=f'<strong>Personal comparison unavailable</strong><p>Earlier {window(s["baseline_window"])}: {s["baseline_observations"]} observed weeks.<br>Recent {window(s["recent_window"])}: {s["recent_observations"]} observed weeks.</p>'
    return f'<section class="answer" data-answer="personal" data-evidence="{e["evidence_id"]}">{content}</section>'

def focused(m,out):
    ev=m['evidence'];own=[c for c in m['claims'] if c['template']=='personal_change'];peers=[c for c in m['claims'] if c['template']=='comparison'];first=next(iter(ev.values()));s=first['summary'];q=m['question'];layout=m['layout'];state={}
    if layout in {'personal','support'}:
        main=personal(own[0],m);own_summary=ev[own[0]['evidence_id']]['summary']
        if layout=='personal':
            p=next(p for p in m['panels'] if p['kind']=='trajectory');main+=save(out,'trajectory',charts.trajectory(ev[p['evidence_id']]))
            recent=[c for c in peers if ev[c['evidence_id']]['window']==own_summary['recent_window']]
            main+=''.join(peer(c,m) for c in recent or peers)
            heading='How did my click rate change?'
            note='Clicks are not effort or learning. Shading: 95% peer-mean CI. Uncertainty for the change was not estimated.'
        else:
            main+='<p>'+h(first['unit'])+'</p>'+''.join(peer(c,m,short=True) for c in peers);heading='Can my recent click rate be compared with my history and peers?'
            note='Unavailable is not zero. Peer intervals concern the peer mean only.'
    elif layout=='references':
        records=[ev[i] for i in m['comparison_ids']]
        options=''.join(f'<option value="{e["evidence_id"]}">{h({"course":"Recent presentation peers","early_stage":"Presentation peers · earlier period","same_prior_attempt":"Same prior-attempt peers"}[e["reference"]])}</option>' for e in records)
        for e in records:
            eid=e['evidence_id'];ss=e['summary'];chart=charts.reference(records,eid);save(out,'reference-'+eid,chart)
            card=f'<section class="answer" data-answer="peer" data-evidence="{eid}"><p>Person {window(e["window"])}<br><b>Reference {window(e["reference_window"])}</b></p><p>Person <strong>{num(ss["focal_mean"])}</strong> · peer <strong>{num(ss["peer_mean"])}</strong><br>Difference <strong>{num(ss["contrast"],True)}</strong></p><p>Peer mean 95% CI [{num(ss["peer_ci_low"])}, {num(ss["peer_ci_high"])}].<br>{e["people"]:,} peers / {e["observations"]:,} person-weeks.</p>{evidence_link(eid)}</section>'
            state[eid]={'card':card,'svg':chart,'reference':e['reference'],'window':e['window'],'reference_window':e['reference_window'],'summary':ss,'evidence_href':f'#evidence-{eid}'}
        initial=records[0]['evidence_id']
        main=f'<section class="switch-excerpt"><label for="reference-select">View saved analysis</label><select id="reference-select">{options}</select><div class="chart" id="reference-chart">{state[initial]["svg"]}</div><div id="reference-result" aria-live="polite">{state[initial]["card"]}</div></section>'
        heading='How does my recent click rate compare across references?';note='Saved results only; no new investigation or calculation. Peer mean intervals do not describe the person or difference. Eligible peer membership can differ across periods.'
    elif layout=='observations':
        p=next(p for p in m['panels'] if p['kind']=='observation_status');e=ev[p['evidence_id']]
        main=f'<section class="answer"><strong>{e["summary"]["focal_observations"]} observed recent weeks</strong><p>Selected peer comparisons have insufficient support.</p></section><p class="provenance-label">Original compiler: observation timeline</p>'+save(out,'observations',charts.observation(e))
        for c in peers:
            e=ev[c['evidence_id']]
            label={'clicks_per_eligible_day':'Clicks / eligible day','nonbanked_submissions':'Non-banked submissions / week','scheduled_no_submission':'Scheduled non-submissions / week'}[e['feature']]
            main+=f'<div class="unavailable-item" data-answer="peer" data-evidence="{e["evidence_id"]}"><span>{label}</span><span>{num(e["summary"]["focal_mean"])}</span></div>'
        main+=f'<p>Presentation peers, {window(first["reference_window"])}:<br>{first["people"]:,} people / {first["observations"]:,} person-weeks.</p>'
        heading='What is available during these recent weeks?';note='Unavailable is not zero. Eligibility is administrative; logging completeness is unknown. Grades unavailable: release times unknown (original compiler context).'
    elif layout=='assessments':
        main=''
        for c in peers:
            e=ev[c['evidence_id']];ss=e['summary']
            main+=f'<section class="answer" data-answer="peer" data-evidence="{e["evidence_id"]}"><b>{h(FEATURES[e["feature"]])}</b><p><strong>{num(ss["focal_mean"])}</strong> per observed week<br>Peer {num(ss["peer_mean"])} · difference {num(ss["contrast"],True)}.<br>Peer mean 95% CI [{num(ss["peer_ci_low"])}, {num(ss["peer_ci_high"])}].</p></section>'
        p=next(p for p in m['panels'] if p['kind']=='assessment_status');main+=save(out,'assessments',charts.assessment(ev[p['evidence_id']]))
        main+=f'<p>{first["summary"]["focal_observations"]} observed focal weeks.<br>Presentation peers, {window(first["reference_window"])}:<br>{first["people"]:,} people / {first["observations"]:,} person-weeks.</p>'
        heading='What do my assessment records show?';note='Marks and banking approval are unavailable. Dated states are snapshots; they do not measure learning or achievement. Intervals describe peer means only.'
    else:raise ValueError(layout)
    surface=f'<article class="figure-surface" data-layout="{layout}"><header><div class="eyebrow">{h(m["label"])} · saved development case</div><h1>{heading}</h1><p>Earlier {window(s["baseline_window"])}<br>Recent {window(s["recent_window"])} · through day {q["cutoff_day"]}</p></header><div class="excerpt-content">{main}</div><aside class="note">{note}</aside><footer>{h(m["method"])}<br>Saved selections · deterministic values</footer></article>'
    return surface,state

def render(m,out):
    out=Path(out);entry=expanded_render(m,out)
    full=(out/'index.html').read_text()
    full=full.replace('Recent minus earlier; no interval was estimated for this change.','Recent minus earlier. Differences are calculated before rounding. Uncertainty for the change was not estimated.')
    (out/'index.html').write_text(full)
    surface,state=focused(m,out)
    a=full.index('<article class="figure-surface"');b=full.index('</article>',a)+len('</article>')
    body=full[:a]+surface+'<p>Pre-draft excerpt. <a href="index.html">Expanded view</a> and all original claims below. Presentation peers are students in the same course offering. Excerpts are not the basis for completeness review.</p>'+full[b:]
    body=body.replace('<body>','<body class="preparation">').replace('</style>',CSS+'</style>')
    a=body.index('<script id="saved-state"');b=body.index('</script>',a)+len('</script>')
    body=body[:a]+'<script id="saved-state" type="application/json">'+json.dumps({'references':state},ensure_ascii=False).replace('<','\\u003c')+'</script>'+body[b:]
    (out/'figure.html').write_text(body)
    return {**entry,'chart_files':[str(p) for p in sorted((out/'charts').glob('*.svg'))],'source_status':m['selection_status'],'excerpts':'Semantic selection: supported personal displays recent selected peers; support-limited personal displays all selected peers, no trajectory; reference shows only actively selected saved comparison; all original content remains in expanded view and provenance.'}

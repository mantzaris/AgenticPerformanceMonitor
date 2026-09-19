"""Small native SVG vocabulary. Every mark uses a saved result-table value."""
import html
import math
import json

INK, TEAL, RUST, GRID = "#192e38", "#176b72", "#a34f2c", "#dbe3e5"


def esc(value):
    return html.escape(str(value), quote=True)


def num(value, signed=False):
    if value is None:
        return "Unavailable"
    text = f"{value:+,.2f}" if signed and value != 0 else f"{value:,.2f}"
    return text.replace("-", "−")


def text(x, y, value, size=19, color=INK, anchor="start", weight=400):
    return f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}">{esc(value)}</text>'


def svg(body, height, title, values):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="600" height="{height}" viewBox="0 0 600 {height}" role="img" aria-label="{esc(title)}" style="font-family:DejaVu Sans,sans-serif;background:#fff">
<title>{esc(title)}</title><metadata>{esc(json.dumps(values,sort_keys=True))}</metadata>
<defs><pattern id="ineligible" width="7" height="7" patternUnits="userSpaceOnUse"><rect width="7" height="7" fill="#edf0f2"/><path d="M-1,1L1,-1M0,7L7,0M6,8L8,6" stroke="#a4b0b8" stroke-width="1"/></pattern></defs>
{body}</svg>'''


def segments(rows, key):
    """Nulls break lines, including ineligible periods; never interpolate them."""
    groups, current = [], []
    for r in rows:
        if r[key] is None:
            if current:
                groups.append(current)
            current = []
        else:
            current.append(r)
    if current:
        groups.append(current)
    return groups


def trajectory(e):
    rows, s = e["trajectory"], e["summary"]
    maximum = max([1.0] + [r[k] for r in rows for k in ("focal_value", "peer_ci_high") if r[k] is not None])
    step = 10 ** math.floor(math.log10(maximum))
    top = math.ceil(maximum / step) * step
    if maximum <= 1:
        top = 1.0
    x = lambda w: 55 + w * 514 / max(1, len(rows) - 1)
    y = lambda v: 228 - v / top * 164
    parts = [text(6, 22, e["unit"], 18)]
    for window, label, fill in [(s["baseline_window"], "Earlier", "#f1f4f5"), (s["recent_window"], "Recent", "#eaf4f3")]:
        left, right = max(51, x(window[0]) - 15), min(584, x(window[1]) + 15)
        parts += [f'<rect x="{left}" y="36" width="{right-left}" height="199" fill="{fill}"/>', text((left + right) / 2, 55, label, 18, anchor="middle")]
    for v in [0, top/2, top]:
        parts += [f'<line x1="51" y1="{y(v)}" x2="585" y2="{y(v)}" stroke="{GRID}"/>', text(45, y(v)+6, f"{v:g}", 18, anchor="end")]
    for r in rows:
        parts.append(text(x(r["week"]), 255, r["week"], 17, anchor="middle"))
    for group in segments(rows, "peer_ci_low"):
        good = [r for r in group if r["peer_ci_high"] is not None]
        points = [(x(r["week"]), y(r["peer_ci_low"])) for r in good] + [(x(r["week"]), y(r["peer_ci_high"])) for r in reversed(good)]
        parts.append('<polygon points="' + ' '.join(f'{a:.2f},{b:.2f}' for a,b in points) + '" fill="#dcebed"/>')
    for key, color in [("peer_mean", TEAL), ("focal_value", RUST)]:
        for group in segments(rows, key):
            points = ' '.join(f'{x(r["week"]):.2f},{y(r[key]):.2f}' for r in group)
            parts.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="3"/>')
            if key == "focal_value":
                for r in group:
                    parts.append(f'<circle cx="{x(r["week"])}" cy="{y(r[key])}" r="4" fill="{color}"/>')
    parts += [text(318, 282, "Week since presentation start", 18, anchor="middle"),
              text(16, 312, "● Person", 18, RUST), text(165, 312, "━ Same-week peers", 18, TEAL)]
    return svg(''.join(parts), 326, "Weekly recorded values, with earlier and recent windows", {"evidence_id":e["evidence_id"],"trajectory":rows,"windows":[s["baseline_window"],s["recent_window"]],"y_domain":[0,top]})


def references(records, selected):
    """Same focal quantity/window required by caller; one common zero-based scale."""
    maxima = [v for e in records for k,v in e["summary"].items() if k in {"peer_ci_high", "peer_mean", "focal_mean"} and v is not None]
    top = max(1, math.ceil(max(maxima, default=1)))
    x = lambda value: 40 + value / top * 515
    parts = []
    for i,e in enumerate(records):
        yy = 52 + i*83
        selected_row = e["evidence_id"] == selected
        parts.append(f'<rect x="6" y="{yy-40}" width="588" height="78" rx="5" fill="{"#eaf4f3" if selected_row else "#fff"}"/>')
        label = {"course":"Presentation peers", "same_prior_attempt":"Same prior-attempt group", "early_stage":"Presentation peers · earlier period"}[e["reference"]]
        parts.append(text(18, yy-14, label + f' · weeks {e["reference_window"][0]}–{e["reference_window"][1]}', 18, weight=600 if selected_row else 400))
        s=e["summary"]
        parts.append(f'<line x1="40" x2="555" y1="{yy+12}" y2="{yy+12}" stroke="{GRID}"/>')
        if s["peer_ci_low"] is not None:
            lo,hi=x(s["peer_ci_low"]),x(s["peer_ci_high"])
            parts.append(f'<path d="M{lo},{yy+5}V{yy+19}M{lo},{yy+12}H{hi}M{hi},{yy+5}V{yy+19}" stroke="{TEAL}" stroke-width="2" fill="none"/>')
        if s["peer_mean"] is not None:
            parts.append(f'<rect x="{x(s["peer_mean"])-5}" y="{yy+7}" width="10" height="10" fill="{TEAL}"/>')
        if s["focal_mean"] is not None:
            parts.append(f'<circle cx="{x(s["focal_mean"])}" cy="{yy+12}" r="5" fill="{RUST}" stroke="white"/>')
    bottom = len(records)*83+19
    for value in [0,top/2,top]:
        parts.append(text(x(value), bottom+13, f"{value:g}", 18, anchor="middle"))
    parts += [text(300,bottom+40,records[0]["unit"],18,anchor="middle"),
              text(20,bottom+71,"● Person",18,RUST),text(160,bottom+71,"■ Peer mean + 95% CI",18,TEAL)]
    return svg(''.join(parts),bottom+87,"Saved reference comparisons on a common scale",{"selected":selected,"y_scale":"categorical","x_domain":[0,top],"records":[{"evidence_id":e["evidence_id"],"feature":e["feature"],"window":e["window"],"reference_window":e["reference_window"],"summary":e["summary"]} for e in records]})


def observation(e):
    rows=e["observation_status"]
    s=e["summary"]
    cell=552/len(rows)
    parts=[text(12,23,"Administrative eligibility & click-record state",19,weight=600)]
    symbols={"recorded_activity":("●", TEAL, "#e2f1ef"),"zero_recorded_activity":("0", "#805722", "#fcf1d8"),"ineligible":("×", "#64747e", "url(#ineligible)"),"unknown":("?", "#624577", "#f1eaf8")}
    for i,r in enumerate(rows):
        a=24+i*cell;symbol,color,fill=symbols[r["observation_status"]]
        parts.extend([text(a+cell/2,54,r["week"],18,anchor="middle"),f'<rect x="{a+2}" y="66" width="{cell-4}" height="44" rx="4" fill="{fill}" stroke="#dbe3e5"/>',text(a+cell/2,96,symbol,23,color,anchor="middle",weight=600)])
    for window,label in [(s["baseline_window"],"Earlier"),(s["recent_window"],"Recent")]:
        a=24+window[0]*cell;b=24+(window[1]+1)*cell
        parts += [f'<path d="M{a+4},118V123H{b-4}V118" stroke="#70818a" fill="none"/>',text((a+b)/2,148,label+f' {window[0]}–{window[1]}',18,anchor="middle")]
    parts += [text(15,184,"● Recorded clicks",18,TEAL),text(311,184,"0 Zero recorded clicks",18,"#805722"),text(15,215,"× Ineligible",18,"#64747e"),text(311,215,"? Unknown state",18,"#624577")]
    return svg(''.join(parts),232,"Week-by-week eligibility and click-record state; not a measure of effort",{"evidence_id":e["evidence_id"],"observation_status":rows,"state_semantics":"The source observation_status denotes click-record state even for assessment features; value denotes the selected feature."})


def assessment(e):
    rows=e["assessment_status"]
    parts=[text(15,26,"Scheduled assessment record states",19,weight=600)]
    state_labels={"nonbanked_submission_recorded":("●",TEAL,"Non-banked submission recorded"),"no_nonbanked_submission_by_week_end":("○","#805722","No non-banked submission by week end"),"ineligible_on_due_date":("×","#64747e","Ineligible on the scheduled due date"),"banked_credit_timing_unknown":("?","#624577","Banked credit timing unknown")}
    for i,r in enumerate(rows):
        yy=62+i*76
        symbol,color,label=state_labels.get(r["state"],("?",INK,r["state"].replace("_"," ")))
        parts += [text(17,yy+13,symbol,25,color),text(53,yy,f'Due day {r["due_day"]} · state as of day {r["as_of_day"]}',19,weight=600),text(53,yy+28,label,18)]
    if not rows:
        parts.append(text(15,66,"No saved scheduled assessment states.",19))
    return svg(''.join(parts),max(103,50+len(rows)*76),"Scheduled assessment states at recorded snapshot dates, not grade results",{"evidence_id":e["evidence_id"],"assessment_status":rows})

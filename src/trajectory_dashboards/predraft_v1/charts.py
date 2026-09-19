"""Native vectors from already selected saved evidence. No new estimates."""
import json,html,math
from ..presentation_v1.charts import segments,num
INK,TEAL,RUST,GRID='#192e38','#176b72','#a34f2c','#dbe3e5'
def text(x,y,label,size=22,color=INK,anchor='start',bold=False):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{600 if bold else 400}">{html.escape(str(label))}</text>'
def svg(parts,height,title,data):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="500" height="{height}" viewBox="0 0 500 {height}" role="img" aria-label="{html.escape(title)}" style="font-family:DejaVu Sans,sans-serif;background:white"><title>{html.escape(title)}</title><metadata>{html.escape(json.dumps(data,sort_keys=True))}</metadata><defs><pattern id="hatch" width="8" height="8" patternUnits="userSpaceOnUse"><rect width="8" height="8" fill="#f1f4f5"/><path d="M0,8L8,0" stroke="#a4b0b8"/></pattern></defs>{''.join(parts)}</svg>'''
def trajectory(e):
    rows=e['trajectory'];s=e['summary'];maximum=max([1]+[r[k] for r in rows for k in ['focal_value','peer_ci_high'] if r[k] is not None]);step=10**math.floor(math.log10(maximum));top=math.ceil(maximum/step)*step
    x=lambda w:45+430*w/max(1,len(rows)-1); y=lambda v:198-128*v/top
    parts=[text(4,23,e['unit'])]
    for w,label,fill in [(s['baseline_window'],'Earlier','#f1f4f5'),(s['recent_window'],'Recent','#eaf4f3')]:
        a=max(40,x(w[0])-12);b=min(490,x(w[1])+12)
        parts += [f'<rect x="{a}" y="35" width="{b-a}" height="166" fill="{fill}"/>',text((a+b)/2,58,label,anchor='middle')]
    for v in [0,top/2,top]:parts += [f'<path d="M40,{y(v)}H490" stroke="{GRID}"/>',text(35,y(v)+7,f'{v:g}',anchor='end')]
    for g in segments(rows,'peer_ci_low'):
        points=[(x(r['week']),y(r['peer_ci_low'])) for r in g]+[(x(r['week']),y(r['peer_ci_high'])) for r in reversed(g)]
        parts += ['<polygon points="'+' '.join(f'{a:.2f},{b:.2f}' for a,b in points)+'" fill="#dcebed"/>']
    for key,color in [('peer_mean',TEAL),('focal_value',RUST)]:
        for g in segments(rows,key):
            parts += ['<polyline points="'+' '.join(f"{x(r['week']):.2f},{y(r[key]):.2f}" for r in g)+f'" stroke="{color}" stroke-width="3" fill="none"/>']
            if key=='focal_value':parts += [f'<circle cx="{x(r["week"])}" cy="{y(r[key])}" r="3.5" fill="{color}"/>' for r in g]
    parts += [text(x(r['week']),226,r['week'],anchor='middle') for r in rows]
    parts += [text(250,255,'Week since course offering began',anchor='middle'),text(8,286,'● Person',color=RUST),text(164,286,'━ Same-week peers',color=TEAL)]
    return svg(parts,300,'Saved weekly trajectory, with gaps preserved',{'evidence_id':e['evidence_id'],'trajectory':rows,'y_domain':[0,top],'windows':[s['baseline_window'],s['recent_window']]})
def observation(e):
    rows=e['observation_status'];s=e['summary'];cell=470/len(rows)
    parts=[text(10,23,'Week / click-record state',bold=True)]
    symbols={'zero_recorded_activity':('0','#805722','#fcf1d8'),'recorded_activity':('●',TEAL,'#e2f1ef'),'ineligible':('×','#64747e','url(#hatch)'),'unknown':('?','#624577','#f1eaf8')}
    for i,r in enumerate(rows):
        a=15+i*cell;symbol,color,fill=symbols[r['observation_status']]
        parts += [text(a+cell/2,56,r['week'],anchor='middle'),f'<rect x="{a+2}" y="67" width="{cell-4}" height="42" rx="3" fill="{fill}" stroke="{GRID}"/>',text(a+cell/2,98,symbol,26,color,anchor='middle',bold=True)]
    for w,label in [(s['baseline_window'],'Earlier'),(s['recent_window'],'Recent')]:
        a=15+w[0]*cell;b=15+(w[1]+1)*cell
        parts += [f'<path d="M{a+3},115V121H{b-3}V115" stroke="#70818a" fill="none"/>',text((a+b)/2,149,f'{label} {w[0]}–{w[1]}',anchor='middle')]
    parts += [text(8,183,'0 Recorded zero',color='#805722'),text(270,183,'× Ineligible',color='#64747e'),text(8,214,'● Recorded clicks',color=TEAL),text(270,214,'? Unknown',color='#624577')]
    return svg(parts,229,'Administrative eligibility and recorded click states',{'evidence_id':e['evidence_id'],'observation_status':rows})
def reference(records,eid):
    e=next(e for e in records if e['evidence_id']==eid);s=e['summary'];top=max(1,math.ceil(max(e['summary'][k] for e in records for k in ['peer_ci_high','peer_mean','focal_mean'] if e['summary'][k] is not None)))
    x=lambda v:28+440*v/top
    parts=[f'<rect x="0" y="0" width="500" height="73" rx="5" fill="#eaf4f3"/>',f'<path d="M28,35H468" stroke="{GRID}"/>']
    lo,hi=x(s['peer_ci_low']),x(s['peer_ci_high'])
    parts += [f'<path d="M{lo},23V47M{lo},35H{hi}M{hi},23V47" stroke="{TEAL}" stroke-width="2" fill="none"/>',f'<rect x="{x(s["peer_mean"])-6}" y="29" width="12" height="12" fill="{TEAL}"/>',f'<circle cx="{x(s["focal_mean"])}" cy="35" r="6" fill="{RUST}" stroke="white"/>']
    parts += [text(x(v),100,f'{v:g}',anchor='middle') for v in [0,top/2,top]]
    parts += [text(250,130,e['unit'],anchor='middle'),text(6,162,'● Person',color=RUST),text(164,162,'■ Peer mean + 95% CI',color=TEAL)]
    return svg(parts,176,'Selected saved reference; fixed focal mean and common scale',{'selected':eid,'x_domain':[0,top],'evidence_id':eid,'summary':s,'reference_window':e['reference_window'],'window':e['window']})
def assessment(e):
    rows=e['assessment_status'];parts=[text(10,24,'Dated assessment states',bold=True)]
    labels={'nonbanked_submission_recorded':('●',TEAL,['Non-banked submission recorded']),'no_nonbanked_submission_by_week_end':('○','#805722',['No non-banked submission','by week end']),'ineligible_on_due_date':('×','#64747e',['Ineligible on scheduled due date'])}
    yy=60
    for r in rows:
        symbol,color,lines=labels.get(r['state'],('?',INK,[r['state'].replace('_',' ')]))
        parts += [text(8,yy+6,symbol,26,color),text(42,yy,f'Due {r["due_day"]} · as of day {r["as_of_day"]}',bold=True)]
        parts += [text(42,yy+28*(i+1),t) for i,t in enumerate(lines)];yy+=40+28*len(lines)
    return svg(parts,yy,'Saved scheduled-assessment snapshots, not grades',{'evidence_id':e['evidence_id'],'assessment_status':rows})

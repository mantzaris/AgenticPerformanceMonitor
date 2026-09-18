"""Construct structural development tasks and a small self-contained source bundle.

Does not read outcomes, scores or any reserved person's longitudinal records.
"""
from pathlib import Path
import shutil
import pandas as pd
from trajectory_dashboards.common import read_json,write_json,file_hash,digest,now
from trajectory_dashboards.stage2.core import ROOT,Registry,Question,append_event


def main():
    destination = ROOT / "tasks/manifest.json"
    if destination.exists():
        raise RuntimeError("Task selection already exists; replay it, do not select again")
    cfg = Registry().cfg
    meta = read_json("artifacts/data/preparation.json")
    for name,h in meta["files"].items():
        if file_hash(Path("data/prepared")/name) != h:
            raise ValueError("Stage 1 source mismatch")
    w = pd.read_parquet("data/prepared/weekly.parquet")
    assignments = read_json("artifacts/data/splits.json")["assignments"]
    assert not set(w.person_id) & set(assignments["reserved"])
    original = {q["person_id"] for q in read_json("artifacts/data/questions.json")}
    used = set(original)
    text = {
        "personal_change": "How has my recent recorded activity changed from my earlier history, and how does it compare with peers?",
        "reference_sensitivity": "Is the direction of my recent activity comparison the same for presentation peers, peers with similar prior-attempt history, and peers at an earlier study stage?",
        "observation_limits": "My recorded activity looks incomplete. What can these records establish, given registration eligibility, unknown logging completeness, and assessment records?",
        "insufficient_support": "Do I have enough recent eligible observations to compare my activity with my earlier history and peers? Please say when the data cannot support a comparison.",
        "assessment_availability": "What do recorded assessment submissions and scheduled non-submissions tell us so far? Can they tell us my marks or learning progress?",
        "alternate_windows": "Using the stated earlier and recent windows, how does my activity compare with my own history and with different peer definitions?"
    }
    layout = [
        ("construction","personal_change","AAA_2013J","standard","adequate"),
        ("construction","reference_sensitivity","BBB_2013B","standard","repeat"),
        ("construction","observation_limits","BBB_2013B","standard","partial"),
        ("construction","insufficient_support","BBB_2013B","standard","insufficient"),
        ("construction","assessment_availability","BBB_2013B","mid","adequate"),
        ("construction","alternate_windows","BBB_2013B","alternate","adequate"),
        ("pilot","personal_change","AAA_2013J","standard","adequate"),
        ("pilot","personal_change","BBB_2013B","mid","adequate"),
        ("pilot","reference_sensitivity","BBB_2013B","standard","repeat"),
        ("pilot","reference_sensitivity","BBB_2013B","standard","first"),
        ("pilot","observation_limits","BBB_2013B","mid","partial"),
        ("pilot","observation_limits","AAA_2013J","standard","partial"),
        ("pilot","insufficient_support","BBB_2013B","short","insufficient"),
        ("pilot","insufficient_support","BBB_2013B","narrow","insufficient"),
        ("pilot","assessment_availability","AAA_2013J","standard","adequate"),
        ("pilot","assessment_availability","BBB_2013B","standard","adequate"),
        ("pilot","alternate_windows","AAA_2013J","mid","adequate"),
        ("pilot","alternate_windows","BBB_2013B","alternate","adequate")
    ]
    tasks = []
    counts = {"construction":0,"pilot":0}
    for subset,kind,course,profile,criterion in layout:
        counts[subset]+=1
        tid = ("c" if subset=="construction" else "p")+f"{counts[subset]:02d}"
        p = cfg["profiles"][profile]
        rows = w[w.course.eq(course) & w.end_day.le(p["cutoff_day"])]
        pool=[]
        for person,g in rows.groupby("person_id"):
            if person in used:
                continue
            n = int(g.eligible_days.gt(0).sum())
            recent = int(g[g.week.between(*p["recent"])].eligible_days.gt(0).sum())
            baseline = int(g[g.week.between(*p["baseline"])].eligible_days.gt(0).sum())
            match = n >= len(g)-1 and min(recent,baseline)>=2
            if criterion == "partial": match = 1 <= n < len(g)-1
            if criterion == "insufficient": match = recent < 2 and baseline >= 1
            if criterion in {"repeat","first"}: match = match and g.prior_attempt_group.iloc[0] == criterion+"_attempt"
            if match: pool.append(int(person))
        if not pool: raise ValueError(f"No structural candidates for {tid}")
        person = min(pool,key=lambda i:digest(["stage2-structural-v1",tid,i]))
        used.add(person)
        q = Question(question_id=tid,kind=kind,text=text[kind]+f" Earlier weeks {p['baseline'][0]}–{p['baseline'][1]}; recent weeks {p['recent'][0]}–{p['recent'][1]}; information through day {p['cutoff_day']}.",person_id=person,course=course,profile=profile,cutoff_day=p["cutoff_day"])
        tasks.append({"subset":subset,"question":q.model_dump(),"selection":{"criterion":criterion,"candidate_people":len(pool),"hash_rule":"minimum SHA256(stage2-structural-v1, task ID, person ID)","synthetic":False}})
    source=ROOT/"source"
    source.mkdir(parents=True,exist_ok=True)
    for name in meta["files"]: shutil.copyfile(Path("data/prepared")/name,source/name)
    write_json(source/"manifest.json",{"created_utc":now(),"files":{n:file_hash(source/n) for n in meta["files"]},"stage1_source_manifest_sha256":file_hash("artifacts/data/preparation.json"),"split_sha256":file_hash("artifacts/data/splits.json"),"excluded_reference_people":sorted(used),"description":"Small allowlisted derived development bundle for independent semantic checks and offline replay; no raw scores/outcomes or reserved trajectories"})
    write_json(destination,{"version":"v1","selected_utc":now(),"tasks":tasks,"reference_population":"Development people in the selected presentation, excluding all 18 task focal people and the three original demonstration people across registrations. All methods share this population.","selection_rule":"Only eligibility counts, prior-attempt category, course and profile; no activity magnitudes, outcomes or model results used.","original_demo_people_excluded":sorted(original),"construction_people":sorted(t['question']['person_id'] for t in tasks if t['subset']=='construction'),"pilot_people":sorted(t['question']['person_id'] for t in tasks if t['subset']=='pilot'),"reserved_people":len(assignments['reserved']),"synthetic_tasks":0})
    append_event({"event":"tasks_selected","tasks":18,"manifest_sha256":file_hash(destination),"source_bundle_sha256":digest(read_json(source/'manifest.json'))})
    print([(t['question']['question_id'],t['question']['person_id'],t['question']['kind'],t['selection']['candidate_people']) for t in tasks])

if __name__ == "__main__": main()

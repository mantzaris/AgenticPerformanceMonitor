"""One declared measurement sensitivity on development data, not a benchmark."""
from pathlib import Path
import numpy as np
import pandas as pd
from trajectory_dashboards.acquire import connection
from trajectory_dashboards.common import read_json, write_json

db = connection()
w = pd.read_parquet("data/prepared/weekly.parquet")
selected = w[["person_id", "course"]].drop_duplicates()
selected["code_module"] = selected.course.str.split("_").str[0]
selected["code_presentation"] = selected.course.str.split("_").str[1]
selected = selected.rename(columns={"person_id": "id_student"})
db.register("selected", selected)
cutoff = read_json("configs/stage1.json")["cutoff_day"]
a = db.execute(f"SELECT v.*,r.date_registration,r.date_unregistration FROM studentVle v JOIN selected s USING(code_module,code_presentation,id_student) JOIN studentRegistration r USING(code_module,code_presentation,id_student) WHERE date BETWEEN 0 AND {cutoff}").df()
a = a[(a.date >= a.date_registration) & (a.date_unregistration.isna() | (a.date_unregistration > cutoff) | (a.date < a.date_unregistration))].copy()
source_key = ["code_module", "code_presentation", "id_student", "id_site", "date", "sum_click"]
dedup = a.drop_duplicates(source_key).copy()
dedup["course"] = dedup.code_module + "_" + dedup.code_presentation
dedup["week"] = dedup.date // 7
counts = dedup.groupby(["id_student", "course", "week"]).sum_click.sum().rename("dedup_clicks").reset_index().rename(columns={"id_student": "person_id"})
alt = w.merge(counts, on=["person_id", "course", "week"], how="left", validate="one_to_one")
alt["dedup_rate"] = alt.dedup_clicks.fillna(0) / alt.eligible_days.replace(0, np.nan)
rows = []
for q in read_json("artifacts/data/questions.json"):
    e = alt[alt.course.eq(q["course"]) & alt.week.between(8,11)]
    focal = e[e.person_id.eq(q["person_id"])]
    peers = e[e.person_id.ne(q["person_id"])]
    one = {"question_id": q["question_id"], "course": q["course"], "window": [8,11], "reference": "course", "unit": "recorded clicks / eligible day"}
    for col,label in [("clicks_per_eligible_day", "preserve_source_rows"), ("dedup_rate", "drop_exact_repeated_rows_sensitivity")]:
        fm = focal[col].mean()
        pm = peers.groupby("person_id")[col].mean().mean()
        one[label] = {"focal_mean": None if pd.isna(fm) else float(fm), "peer_mean": float(pm), "contrast": None if pd.isna(fm) else float(fm-pm)}
    rows.append(one)
write_json("artifacts/data/duplicate_sensitivity.json", {"scope": "Selected development registrations; eligible days <=83 only. All source rows retained in main path. This alternative is not asserted to be a correction.", "source_rows": len(a), "exact_duplicate_excess": len(a)-len(dedup), "examples": rows, "limitation": "Equal student/site/day/count records need not be accidental duplication; absent event IDs make true unique events unidentifiable. This analysis measures one preprocessing sensitivity, not the truth of either interpretation."})
print(rows)

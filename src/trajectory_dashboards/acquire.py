"""Download the creator-deposited UCI archive; audit keys before any joins."""
from __future__ import annotations

import urllib.request
import zipfile
from pathlib import Path
import duckdb
import pandas as pd
from .common import file_hash, now, write_json
from .contracts import DatasetManifest

SOURCE = "https://archive.ics.uci.edu/static/public/349/open+university+learning+analytics+dataset.zip"
EXPECTED_ARCHIVE_SHA256 = "f2ed1902616c1fe8d2824d872c0b7d2d72be435bf0124d077044fe4be2c6d3e4"
KEYS = {
    "courses": ["code_module", "code_presentation"],
    "assessments": ["id_assessment"],
    "vle": ["code_module", "code_presentation", "id_site"],
    "studentInfo": ["code_module", "code_presentation", "id_student"],
    "studentRegistration": ["code_module", "code_presentation", "id_student"],
    "studentAssessment": ["id_assessment", "id_student"],
    "studentVle": ["code_module", "code_presentation", "id_student", "id_site", "date"],
}


def acquire(root=Path("data/raw")):
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    archive = root / "oulad.zip"
    if not archive.exists():
        temporary = archive.with_suffix(".partial")
        urllib.request.urlretrieve(SOURCE, temporary)
        temporary.rename(archive)
        write_json(root / "retrieval.json", {"retrieved_utc": now(), "source": SOURCE})
    if file_hash(archive) != EXPECTED_ARCHIVE_SHA256:
        raise ValueError("Source archive changed; review before using a new data version")
    with zipfile.ZipFile(archive) as z:
        for item in z.infolist():
            if Path(item.filename).name != item.filename:
                raise ValueError("Unexpected archive path")
            if not (root / item.filename).exists():
                z.extract(item, root)
    print(f"Archive verified: {file_hash(archive)}", flush=True)


def connection(root=Path("data/raw")):
    db = duckdb.connect()
    db.execute("SET threads=4")
    for table in KEYS:
        p = str((Path(root) / (table + ".csv")).resolve()).replace("'", "''")
        db.execute(f"CREATE VIEW {table} AS SELECT * FROM read_csv_auto('{p}', sample_size=-1, nullstr=['', '?'])")
    return db


def audit(root=Path("data/raw"), output=Path("artifacts/data")):
    root, output = Path(root), Path(output)
    db = connection(root)
    files = {}
    for table, keys in KEYS.items():
        columns = db.execute(f"DESCRIBE {table}").fetchall()
        n = db.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
        key = ",".join(keys)
        dup = db.execute(f"SELECT coalesce(sum(n-1),0) FROM (SELECT count(*) n FROM {table} GROUP BY {key} HAVING count(*)>1)").fetchone()[0]
        nulls = db.execute("SELECT " + ",".join(f'count(*) FILTER (WHERE "{c[0]}" IS NULL)' for c in columns) + f" FROM {table}").fetchone()
        files[table + ".csv"] = {"sha256": file_hash(root / (table + ".csv")), "bytes": (root / (table + ".csv")).stat().st_size, "rows": n, "schema": {c[0]: c[1] for c in columns}, "candidate_key": keys, "duplicate_excess_rows": int(dup), "missing": dict(zip([c[0] for c in columns], nulls))}
        print(f"Audited {table}: {n} rows, {dup} duplicate key excess", flush=True)
    relationships = {}
    joins = [
        ("info_registration", "studentInfo", "studentRegistration", ["code_module", "code_presentation", "id_student"]),
        ("assessment_definition", "studentAssessment", "assessments", ["id_assessment"]),
        ("interaction_resource", "studentVle", "vle", ["code_module", "code_presentation", "id_site"]),
        ("interaction_registration", "studentVle", "studentRegistration", ["code_module", "code_presentation", "id_student"]),
    ]
    for name, left, right, keys in joins:
        cond = " AND ".join(f"l.{k}=r.{k}" for k in keys)
        joined, unmatched = db.execute(f"SELECT count(*), count(*) FILTER (WHERE r.{keys[0]} IS NULL) FROM {left} l LEFT JOIN {right} r ON {cond}").fetchone()
        source = files[left + ".csv"]["rows"]
        relationships[name] = {"left_rows": source, "left_join_rows": joined, "unmatched_rows": unmatched, "multiplication": joined - source, "key": keys}
        if joined != source:
            raise ValueError(f"Join multiplication: {name}")
    relationships["assessment_registration_unmatched"] = db.execute("SELECT count(*) FROM studentAssessment s JOIN assessments a USING(id_assessment) ANTI JOIN studentRegistration r USING(code_module,code_presentation,id_student)").fetchone()[0]
    counts = {
        "distinct_students": db.execute("SELECT count(DISTINCT id_student) FROM studentInfo").fetchone()[0],
        "student_course_registrations": files["studentInfo.csv"]["rows"],
        "student_assessments": files["studentAssessment.csv"]["rows"],
        "course_presentations": db.execute("SELECT * FROM courses ORDER BY code_module,code_presentation").df().to_dict("records"),
        "people_with_multiple_registrations": db.execute("SELECT count(*) FROM (SELECT id_student FROM studentInfo GROUP BY id_student HAVING count(*)>1)").fetchone()[0],
        "banked_assessments": db.execute("SELECT count(*) FROM studentAssessment WHERE is_banked=1").fetchone()[0],
        "withdrawal_recorded": db.execute("SELECT count(*) FROM studentRegistration WHERE date_unregistration IS NOT NULL").fetchone()[0],
        "unknown_registration_date": db.execute("SELECT count(*) FROM studentRegistration WHERE date_registration IS NULL").fetchone()[0],
        "registration_date_range": list(db.execute("SELECT min(date_registration),max(date_registration),min(date_unregistration),max(date_unregistration) FROM studentRegistration").fetchone()),
        "interaction_date_range": list(db.execute("SELECT min(date),max(date) FROM studentVle").fetchone()),
        "submission_date_range": list(db.execute("SELECT min(date_submitted),max(date_submitted) FROM studentAssessment").fetchone()),
        "interaction_repetitions": db.execute("SELECT min(n) min_rows, median(n) median_rows, max(n) max_rows, min(n_days) min_days, median(n_days) median_days, max(n_days) max_days FROM (SELECT id_student,code_module,code_presentation,count(*) n,count(DISTINCT date) n_days FROM studentVle GROUP BY ALL)").df().to_dict("records")[0],
        "interaction_exact_duplicate_excess": db.execute("SELECT coalesce(sum(n-1),0) FROM (SELECT code_module,code_presentation,id_student,id_site,date,sum_click,count(*) n FROM studentVle GROUP BY code_module,code_presentation,id_student,id_site,date,sum_click HAVING count(*)>1)").fetchone()[0],
    }
    for p in root.iterdir():
        if p.name not in files and p.suffix not in {".zip", ".json"}:
            files[p.name] = {"sha256": file_hash(p), "bytes": p.stat().st_size}
    from .common import read_json
    manifest = DatasetManifest(dataset="OULAD creator-deposited UCI archive 349", source_url=SOURCE,
        retrieved_utc=read_json(root / "retrieval.json")["retrieved_utc"], license="CC BY 4.0",
        attribution="Kuzilek, Hlosta, Zdrahal (2015), DOI:10.24432/C5KK69; source data unmodified; weekly derived summaries added.",
        archive_sha256=file_hash(root / "oulad.zip"), files=files, counts=counts, relationships=relationships,
        time_semantics={"origin": "Day 0 is presentation start; negative dates are before start.", "date": "Daily VLE aggregate day or scheduled assessment day (table dependent).", "date_submitted": "Submission day, not grade availability.", "date_registration": "Administrative registration day; null means unknown.", "date_unregistration": "Withdrawal day; future values are censored at the query cutoff.", "presentation": "B starts February; J starts October; code is not an equal-length measurement scale.", "scores": "No release timestamp; withheld from prospective features.", "banking": "Credit from earlier attempts; approval availability unknown; excluded from non-banked submissions."},
        observation_states={"recorded_activity": "Positive recorded clicks within eligible days.", "zero_recorded_activity": "No positive recorded clicks; logging completeness unknown.", "ineligible": "No administratively eligible day in this week.", "unknown": "Registration date unavailable; values withheld.", "scheduled_no_submission": "Scheduled non-exam assessment due while eligible with no non-banked submission recorded by week end; exemptions unknown."})
    write_json(output / "manifest.json", manifest.model_dump())
    text = ["# OULAD audit", "", f"Retrieved {manifest.retrieved_utc}; CC BY 4.0. Source: {SOURCE}", "", f"Observed **{counts['distinct_students']:,} distinct people**, **{counts['student_course_registrations']:,} registrations**, **{counts['student_assessments']:,} assessment records**. These are independently counted, not hard-coded expectations.", "", "| Table | Rows | Duplicate key excess | Missing values |", "| --- | ---: | ---: | --- |"]
    for name, f in files.items():
        if "rows" in f:
            text.append(f"| {name} | {f['rows']} | {f['duplicate_excess_rows']} | { {k:v for k,v in f['missing'].items() if v} } |")
    text += ["", "All audited many-to-one left joins preserve row counts. Detailed keys, unmatched rows, schemas, repeated-observation counts, ranges and hashes are in manifest.json. Never join submissions and clicks directly by person: that is many-to-many. Aggregate each stream before joining to the person/course/week grid.", "", f"The interaction candidate key is NOT unique. There are {counts['interaction_exact_duplicate_excess']} exact repeated-row excess records. The pipeline preserves source rows and sums recorded counts; it does not assert these are uniquely identifiable click events. A deduplication sensitivity check is required before substantive activity interpretation. The archive data dictionary also states 32953 registrations in one section, while its class totals and actual CSV give 32593; observed CSV counts take precedence.", "", f"{counts['people_with_multiple_registrations']} people have multiple registrations; {counts['banked_assessments']} assessment rows are banked; {counts['withdrawal_recorded']} registrations record withdrawal; {counts['unknown_registration_date']} lack registration dates.", "", "The global audit may inspect retrospective fields for data quality. Prospective preparation uses a separate explicit allowlist and censors future information. Counts of clicks are neither effort nor time studying. Missing click rows do not diagnose logging failure.", "", "Source attribution: Kuzilek, Hlosta and Zdrahal, UCI dataset DOI 10.24432/C5KK69. Raw data are excluded from Git."]
    output.mkdir(parents=True, exist_ok=True)
    (output / "AUDIT.md").write_text("\n".join(text) + "\n")
    db.close()
    return manifest

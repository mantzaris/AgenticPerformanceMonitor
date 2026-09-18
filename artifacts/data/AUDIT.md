# OULAD audit

Retrieved 2026-09-18T16:14:52.928113+00:00; CC BY 4.0. Source: https://archive.ics.uci.edu/static/public/349/open+university+learning+analytics+dataset.zip

Observed **28,785 distinct people**, **32,593 registrations**, **173,912 assessment records**. These are independently counted, not hard-coded expectations.

| Table | Rows | Duplicate key excess | Missing values |
| --- | ---: | ---: | --- |
| courses.csv | 22 | 0 | {} |
| assessments.csv | 206 | 0 | {'date': 11} |
| vle.csv | 6364 | 0 | {'week_from': 5243, 'week_to': 5243} |
| studentInfo.csv | 32593 | 0 | {'imd_band': 1111} |
| studentRegistration.csv | 32593 | 0 | {'date_registration': 45, 'date_unregistration': 22521} |
| studentAssessment.csv | 173912 | 0 | {'score': 173} |
| studentVle.csv | 10655280 | 2195960 | {} |

All audited many-to-one left joins preserve row counts. Detailed keys, unmatched rows, schemas, repeated-observation counts, ranges and hashes are in manifest.json. Never join submissions and clicks directly by person: that is many-to-many. Aggregate each stream before joining to the person/course/week grid.

The interaction candidate key is NOT unique. There are 787170 exact repeated-row excess records. The pipeline preserves source rows and sums recorded counts; it does not assert these are uniquely identifiable click events. A deduplication sensitivity check is required before substantive activity interpretation. The archive data dictionary also states 32953 registrations in one section, while its class totals and actual CSV give 32593; observed CSV counts take precedence.

3538 people have multiple registrations; 1909 assessment rows are banked; 10072 registrations record withdrawal; 45 lack registration dates.

The global audit may inspect retrospective fields for data quality. Prospective preparation uses a separate explicit allowlist and censors future information. Counts of clicks are neither effort nor time studying. Missing click rows do not diagnose logging failure.

Source attribution: Kuzilek, Hlosta and Zdrahal, UCI dataset DOI 10.24432/C5KK69. Raw data are excluded from Git.

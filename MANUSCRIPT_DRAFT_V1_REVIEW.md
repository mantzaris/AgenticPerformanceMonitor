# Manuscript Draft V1 — author review

**[Read the complete 12-page manuscript](paper/draft_v1/main.pdf).**
Title: *Evidence-Grounded Agentic Dashboards: Numerical Validity, Answer
Completeness, and Adaptive Presentation*.

This is an anonymous ICAART 2027 regular-paper author-review draft, not a
submission-readiness declaration. It contains full prose, five figures, three
source-generated tables, and 15 verified bibliography entries. No submission or
conference/reviewer contact occurred.

Work started on clean `main` at
`7db871fe445904af3edea8753931ceff78ce6cc7`. The handoff is committed directly to
`main` under the repository workflow. Resolve its commit with:

```sh
git log -1 --format=%H -- MANUSCRIPT_DRAFT_V1_REVIEW.md
```

## Argument and evidence

Correct numerical evidence does not ensure that a dashboard answers the requested
feature, window and comparison. The article studies the responsibilities of the
agent, deterministic tools, binding/validation, compiler context and later
adaptive presentation. The principal controlled evidence is the frozen 24-person
development comparison, not a pooled trend across stages.

| Frozen endpoint | Enumeration | A: compact | B: derived metadata | C: explicit binding |
| --- | ---: | ---: | ---: | ---: |
| Complete visible answers | 24/24 | 21/24 | 15/24 | 15/24 |
| Complete through method selections | 24/24 | 18/24 | 14/24 | 11/24 |

Tables and result macros are generated from frozen machine-readable reports.
Explicit binding did not improve the frozen endpoint; enumeration remains complete
and cheaper within the predefined registry. B17–20 contain requested recent means
that the frozen predicate does not credit. Those scores remain unchanged; this
limitation is prominent in the abstract, figure caption and results discussion.
B–A changes an interface package, including catalogue access. No isolated metadata
effect, unrestricted understanding, usability gain or general reliability is claimed.

## Deliverables

- [LaTeX entry point](paper/draft_v1/main.tex), [organized sections](paper/draft_v1/sections/),
  [bibliography](paper/draft_v1/references.bib), [build README](paper/draft_v1/README.md).
- [Publication figures](paper/draft_v1/figures/), [generated tables and provenance](paper/draft_v1/generated/).
  The assessment figure is retained as an unused author-review candidate;
  the main paper does not rely on a supplement.
- [All page proofs](paper/draft_v1/checks/pages.html),
  [page-by-page inspection](paper/draft_v1/review/INSPECTION.md).
- [Claim-to-evidence and asset map](paper/draft_v1/review/CLAIM_TO_EVIDENCE.md),
  [primary-source reference checks](paper/draft_v1/review/REFERENCES_VERIFIED.md),
  [current venue/template verification](paper/draft_v1/review/VENUE_AND_TEMPLATE.md).
- [Specific decisions before submission](paper/draft_v1/DECISIONS_BEFORE_SUBMISSION.md).
  The [96-slot human-review packet](artifacts/predraft_v1/human_review/index.html)
  remains unchanged and pending.

## Reproduction and verification

From the repository root in the existing environment:

```sh
python3 paper/draft_v1/scripts/build.py
.venv/bin/python paper/draft_v1/scripts/browser_proof.py --chromium /snap/bin/chromium
python3 paper/draft_v1/scripts/verify.py
```

The first command builds the complete PDF; the others reproduce the CPU browser
proof/count and focused checks. No model, analytical dispatcher or evaluator runs.
See the README for dependencies and a LaTeX-only build. A direct PDF/HTML viewer
is sufficient for review; no server is required.

| Verification | Result |
| --- | --- |
| Official template | PASS: fresh official archive matches preserved SHA256; used class/style files unchanged. Text width 158.0134 mm, column gap 8 mm. |
| Compilation | PASS: 12 A4 pages, five figures, three tables, 15 resolved references; all fonts embedded; no overfull boxes, missing glyphs or undefined citations/references. |
| Page inspection | PASS: every page rendered, opened in Chromium and visually inspected; figures retain at least 8 pt critical text. Author review is still required. |
| Length | 40,349 non-whitespace characters including raster figure text; 40,849 with a 500-glyph allowance, inside the current 10,000–50,000 range. This is an estimate, not the submission counter. |
| Anonymity/disclosure | PASS for implemented checks: no author identity, identifying repository URL or author PDF metadata; truthful Codex disclosure and citations present. Final disclosure placement needs author confirmation. |
| Frozen outcomes and failures | PASS: all 96 slots and disputed scores retained; incomplete A15 preserved; tables/categories agree with original reports. |
| Preservation | PASS: all 7,711 initially tracked files unchanged, including experiments and blank review forms. New work is confined to this entry point and `paper/draft_v1/`. |
| Rebuild | PASS: second full build reproduces all 15 checked PDF/figure/table outputs byte for byte in the recorded environment. |

Machine records: [verification](paper/draft_v1/checks/verification.json),
[rebuild](paper/draft_v1/checks/reproducibility.json),
[count](paper/draft_v1/checks/character_count.json),
[browser](paper/draft_v1/checks/browser.json),
[drafting manifest](paper/draft_v1/checks/run_manifest.json).

## Remaining decisions and stop boundary

Before submission, authors need answer-equivalence adjudication (especially B17–20
and C21/C23), scientific review of measures/support/references, a decision about
the intended claim and any fixed held-out study, and confirmation of venue
disclosure/anonymity arrangements. The internal engineering gate is not a
conference acceptance criterion. Source checks and automated inspection are not
independent human review.

No new experimental inference, GPU process, reserved-observation access, evaluator
change or final validation occurred. CPU build/browser processes completed and
the owned browser was closed; no local server was started. This stage ends with
the complete draft, without submission or a further research stage.

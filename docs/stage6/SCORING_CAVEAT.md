# Post-freeze display/scoring discrepancy — primary scores unchanged

During the declared browser/trace inspection, B cases **17–20** displayed both
requested recent assessment means in supported personal-change claims. The frozen
Stage 3 `assess_item` predicate for a `focal` requirement credits a comparison
panel or supported comparison claim, but does not inspect a personal-change claim.
It therefore marks these eight requested mean items as retrieved-but-omitted.
This is a concrete equivalent-answer-form limitation, not a numerical failure.

| Case | Displayed recent nonbanked submissions/week | Displayed recent scheduled non-submissions/week | Window |
| --- | ---: | ---: | --- |
| s6_17 | 0.25 | 0.00 | weeks 8–11 |
| s6_18 | 0.00 | 0.00 | weeks 8–11 |
| s6_19 | 0.25 | 0.00 | weeks 8–11 |
| s6_20 | 0.25 | 0.00 | weeks 8–11 |

Each claim names its feature, units, recent window and four observed weeks. The
source-bound validator confirms these values. Dated assessment context is selected;
grade availability is supplied by shared compiler context. The first case is in
the prespecified human packet and screenshot selection. All four records and
claims are linked in `artifacts/stage6/inspection/trace_review.json`.

No evaluator, rubric, output or primary score was changed after freeze. **B remains
15/24 in the primary report**, with 14/24 model-selected completeness. It would be
misleading to describe all four pages as literally lacking the requested means.
Crediting only these four disputed cases would raise visible completeness to
19/24; that is a conditional arithmetic bound, not an adopted revised score or
independent adjudication. B would still miss 22/24 and still answer both separate
insufficiency questions on only 2/4 cases. Compiler-supplied grade context also
prevents treating those four as completely model-selected answers.

Human review should also decide whether separately displayed earlier/recent focal
means in peer-comparison claims (for example C21) adequately answer an explicit
personal-change request without a personal contrast. The frozen rule does not
credit that form. This is a separate interpretation question, not an automatic
correction. Explicit separate personal/peer insufficiency remains missing in the
flagged insufficiency cases; no template adjustment alone inserts those answers.

Three mechanism annotations supplement the preserved automatic taxonomy: C12 selects
a valid **baseline** click-rate answer for a requested recent focal mean (the
frozen mismatch helper only classifies peer/personal items); B23 hits the common
11-versus-10 panel limit before its successful repair (the automatic taxonomy
labels its multiline Pydantic error as schema, not layout). A22 also has an invalid descriptive-conclusion scope that the automatic scope
pattern misses. These annotations do not change validity or coverage scores.

External scientific review and a separately versioned, openly labeled post-hoc
scoring audit are required before publication or final validation. There was no
post-freeze tuning, agent rerun or use of evaluator feedback in a prompt/compiler.

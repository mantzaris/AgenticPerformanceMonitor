# Presentation v2 — saved dashboards and figure package

**Implemented, browser inspected and exported.** This separate package reuses
the existing evidence mapper and template-sized chart vocabulary, adds responsive
reading views, explicit historical output status, responsibility disclosure and
bookmarkable saved-reference interaction. It changes no experimental answers,
scores or manuscript figures.

Starting commit: `dd4023f01e8f717cf005f7394e33ac35ab34cf12`, clean `main`.
Work follows `AGENTS.md`: commit and push to `origin main`, without force.
Resolve this handoff commit with `git log -1 --format=%H -- PRESENTATION_V2_REVIEW.md`;
the completion message reports the full SHA and actual push status.

## Open the package

- [Local gallery](artifacts/presentation_v2/gallery/index.html).
- [Figure 1: personal and observation adaptation — PDF](artifacts/presentation_v2/figures/figure1.pdf),
  [PNG](artifacts/presentation_v2/figures/figure1.png), [size proof](artifacts/presentation_v2/figures/figure1.html).
- [Figure 2: controlled saved-reference change — PDF](artifacts/presentation_v2/figures/figure2.pdf),
  [PNG](artifacts/presentation_v2/figures/figure2.png), [size proof](artifacts/presentation_v2/figures/figure2.html).
- [Figure S1: correct numbers, incomplete answer — PDF](artifacts/presentation_v2/figures/figureS1.pdf),
  [PNG](artifacts/presentation_v2/figures/figureS1.png), [size proof](artifacts/presentation_v2/figures/figureS1.html).
- [Figure S2: reference and assessment adaptation — PDF](artifacts/presentation_v2/figures/figureS2.pdf),
  [PNG](artifacts/presentation_v2/figures/figureS2.png), [size proof](artifacts/presentation_v2/figures/figureS2.html).
- [Four-view 2×2 reduction trial](artifacts/presentation_v2/figures/figure1_grid.html),
  [PDF](artifacts/presentation_v2/figures/figure1_grid.pdf), [PNG](artifacts/presentation_v2/figures/figure1_grid.png).
  Its 5.17 pt text is too small; use the paired alternatives, not this trial.
- [Four-page official-template figure proof](artifacts/presentation_v2/proof/layout.pdf),
  [browser proof pages](artifacts/presentation_v2/proof/index.html), [LaTeX](artifacts/presentation_v2/proof/layout.tex).
- [Captions](docs/presentation_v2/CAPTIONS.md), [semantic/provenance contract](docs/presentation_v2/SEMANTICS.md),
  [inspection record](docs/presentation_v2/INSPECTION.md), [reproduction](docs/presentation_v2/REPRODUCTION.md).

## Adaptive views

All four requested examples use compact A without replacement. Stable anonymous
labels are visible; original person/course/question IDs remain in the manifests.

| View / source | What adapts | Open / export |
| --- | --- | --- |
| A: s6_01 personal | Earlier/recent means and supported personal change, highlighted trajectory, separate selected recent and earlier peer cards. | [View](artifacts/presentation_v2/gallery/personal/index.html), [excerpt](artifacts/presentation_v2/gallery/personal/figure.html), [PNG](artifacts/presentation_v2/captures/personal.png), [SVG](artifacts/presentation_v2/gallery/personal/charts/predraft-trajectory.svg) |
| B: s6_05 references | Three selected definitions share a scale; selector, result, windows, counts and evidence link change together. Exact saved state can be bookmarked. | [View](artifacts/presentation_v2/gallery/references/index.html), [excerpt](artifacts/presentation_v2/gallery/references/figure.html), [PNG](artifacts/presentation_v2/captures/references.png) |
| C: s6_09 observations | Explicit unavailability, recorded zero and ineligibility. Compiler-supplied timeline and historical repaired status stay visible. | [View](artifacts/presentation_v2/gallery/observations/index.html), [excerpt](artifacts/presentation_v2/gallery/observations/figure.html), [PNG](artifacts/presentation_v2/captures/observations.png), [SVG](artifacts/presentation_v2/gallery/observations/charts/predraft-observations.svg) |
| D: s6_17 assessments | Weekly submission measures and dated record states; marks/learning limits remain explicit. | [View](artifacts/presentation_v2/gallery/assessments/index.html), [excerpt](artifacts/presentation_v2/gallery/assessments/figure.html), [PNG](artifacts/presentation_v2/captures/assessments.png), [SVG](artifacts/presentation_v2/gallery/assessments/charts/predraft-assessments.svg) |
| E: s6_15 failure / enumeration | Same question; original earlier peer selections remain earlier, while enumeration explicitly answers recent-peer insufficiency. | [Agent](artifacts/presentation_v2/gallery/incomplete/index.html), [enumeration](artifacts/presentation_v2/gallery/baseline/index.html), [agent capture](artifacts/presentation_v2/captures/incomplete.png), [baseline capture](artifacts/presentation_v2/captures/baseline.png) |

Each view preserves access to all original claims, panels, caveats, multiplicities,
conclusion and evidence. Layout dispatch uses selected semantic content, not case
IDs. Exact duplicate personal claims alone are consolidated. The new renderer does
not inspect rubrics or the unselected tool-result dictionary, add missing answers,
or replace an earlier selected window with the requested recent one.

The reference interaction views **saved analysis only**. Figure 2 switches recent
presentation peers to earlier-period peers while retaining focal rate 3.50, weeks
8–11 and scale 0–8. Peer membership/counts can differ across periods. An unknown
reference URL shows an unavailable state rather than a substituted answer.

## Scientific meaning and figure production

The agent selected answer content; deterministic tools calculated every value;
the original compiler supplied tagged wording/context; this presentation changes
layout, labels and emphasis. S1 annotations are outside the faithful interface
captures. Correct source-bound values do not establish answer completeness.

Intervals remain 95% peer-mean bootstrap intervals, not prediction or contrast
intervals. Personal change has no estimated interval. Null is unavailable, not
zero; administrative eligibility and unknown logging completeness remain distinct.
Assessment snapshots retain their as-of dates and do not establish achievement.

The verified official template width is **158.0134 mm**, with an **8 mm** gap.
Preferred candidates have minimum critical text of 8.50, 8.80, 8.54 and 8.27 pt
(Figures 1, 2, S1 and S2). UI PDFs contain raster browser captures plus vector labels;
the 56 standalone SVGs are genuine vectors. Composite PNGs are 300 dpi; capture
device scale is 3. Font, viewport, selector/crop, state and source hashes are in the
[capture manifest](artifacts/presentation_v2/capture_manifest.json).

[Source manifest](artifacts/presentation_v2/source_manifest.json) ·
[figure manifest](artifacts/presentation_v2/figure_manifest.json) ·
[production metadata](artifacts/presentation_v2/run_metadata.json).

## Checks actually performed

| Check | Result / evidence |
| --- | --- |
| Historical preservation | PASS: all 7,799 tracked starting files unchanged, including the manuscript, frozen experiments and review forms. [Inventory](artifacts/presentation_v2/historical_inventory.json) |
| Focused semantic/mapping tests | PASS: 22 tests. [Log](artifacts/presentation_v2/checks/tests.txt) |
| Historical numerical validation/replay | PASS: six saved dashboards, 15 evidence bindings; no analytical dispatcher or scoring call. [Verification](artifacts/presentation_v2/checks/verification.json) |
| Browser controls and sources | PASS: twelve routes, all three references in both routes, permalink restore, unknown-ID handling, original claims, values, counts and interval endpoints. 23 captures. [Manifest](artifacts/presentation_v2/capture_manifest.json) |
| Final-size browser inspection | PASS for four preferred figures; grid trial rejected for readability. Five candidates and four template pages inspected, with no browser errors, external requests or broken links. [Browser record](artifacts/presentation_v2/checks/browser_review.json) |
| Reproduction | PASS: 103/103 exported captures/charts/figures/proof assets byte-identical in a fresh output directory. [Comparison](artifacts/presentation_v2/checks/reproduction.json) |

Two initial capture-check assumptions and an early composition invocation were
corrected; the final checks do not relax scientific validation. Details and the
mobile-label inspection adjustment are in the inspection record.

## Preview and regenerate

```sh
python3 -m http.server 8765 --bind 127.0.0.1 --directory .
# Open http://127.0.0.1:8765/artifacts/presentation_v2/gallery/index.html
# Ctrl-C stops the optional preview server.

python3 scripts/presentation_v2/regenerate.py --inspect
.venv/bin/python -m pytest -q tests/presentation_v2 tests/presentation_v1
.venv/bin/python scripts/presentation_v2/verify.py --replay
```

The gallery also works directly as local files. No preview server was started
during delivery. Browsers launched by the capture/review commands were closed.
No GPU or model process was started; no RunPod access, new inference, reserved-data
access, evaluator change or final validation occurred. The temporary reproduction
tree was removed after verification.

This is presentation of saved development examples, not evidence of improved
accuracy or usability. Scientific review/scoring caveats remain unresolved;
screen proof is not a calibrated physical print. Prior packages and manuscript
draft v1 remain unchanged. The stage stops with these candidate figures.

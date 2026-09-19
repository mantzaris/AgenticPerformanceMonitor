# Saved-development dashboard presentation and figure package

The presentation package is implemented and browser inspected. It provides four
semantic views, a working saved-reference selector, a faithful incomplete-answer
example and publication figure candidates. This is **new presentation of saved
development results**, not improved agent accuracy, a usability result or final
validation.

Work is on `main`, starting from
`960c1dec9ccef105c2b6f23125be6e54a55847bf`. The final delivery commit is the commit
containing this review; `git log -1 --format=%H -- PRESENTATION_V1_REVIEW.md` identifies
it. The completion message reports the final pushed SHA. No historical source or
artifact was edited. All new work is in `presentation_v1` paths plus this entry point.

## Open the package

- [Local gallery](artifacts/presentation_v1/gallery/index.html).
- [Figure 1: personal and reference adaptation — PDF](artifacts/presentation_v1/figures/figure1.pdf),
  [PNG](artifacts/presentation_v1/figures/figure1.png),
  [paper-size browser proof](artifacts/presentation_v1/figures/figure1.html).
- [Figure 2: saved reference change — PDF](artifacts/presentation_v1/figures/figure2.pdf),
  [PNG](artifacts/presentation_v1/figures/figure2.png),
  [proof](artifacts/presentation_v1/figures/figure2.html).
- [Figure S1: correct numbers, incomplete answer — PDF](artifacts/presentation_v1/figures/figureS1.pdf),
  [PNG](artifacts/presentation_v1/figures/figureS1.png),
  [proof](artifacts/presentation_v1/figures/figureS1.html).
- [Figure S2: observation and assessment adaptation — PDF](artifacts/presentation_v1/figures/figureS2.pdf),
  [PNG](artifacts/presentation_v1/figures/figureS2.png),
  [proof](artifacts/presentation_v1/figures/figureS2.html).
- [Four-panel reduction proof](artifacts/presentation_v1/figures/figure1_grid.html),
  [PNG](artifacts/presentation_v1/figures/figure1_grid.png),
  [PDF](artifacts/presentation_v1/figures/figure1_grid.pdf).
- [Captions](docs/presentation_v1/CAPTIONS.md),
  [content/provenance contract](docs/presentation_v1/SEMANTICS.md),
  [exact reproduction and environment](docs/presentation_v1/REPRODUCTION.md).

The 2 × 2 layout was tried and retained for review. Fitting it into an assumed
180 × 240 mm publication area reduces critical text to about 5.4 pt. The preferred
two-panel Figure 1 and Figure S2 retain approximately 8.0 pt critical text at
180 mm width. Individual captures use device scale factor 3; composites use
300 dpi. PDFs contain raster browser captures plus vector editorial labels.
The separately exported native SVG charts are genuine vectors.
PDF exports are marked as binary within this package so Git does not display
their compressed contents as text diffs.

## Views and source relationship

All four main examples use the user-specified compact-A condition. No replacement
selection or attractive-outcome search was needed. Case labels are anonymous;
original person/course/question identifiers and hashes are retained in the
[source manifest](artifacts/presentation_v1/source_manifest.json).

| View | Source | What adapts | Outputs |
| --- | --- | --- | --- |
| A: personal progress | compact_a / s6_01 | Earlier/recent means and change; highlighted timeline; personal and peer scopes separated. One exact personal-claim duplicate is consolidated. | [Expanded](artifacts/presentation_v1/gallery/personal/index.html), [compact](artifacts/presentation_v1/gallery/personal/figure.html), [PNG](artifacts/presentation_v1/captures/personal.png), [trajectory SVG](artifacts/presentation_v1/gallery/personal/charts/focus-trajectory.svg) |
| B: reference comparison | compact_a / s6_05 | Aligned comparisons on a common scale; saved reference selector updates result, highlight, window and evidence link. | [Expanded](artifacts/presentation_v1/gallery/references/index.html), [compact](artifacts/presentation_v1/gallery/references/figure.html), [PNG](artifacts/presentation_v1/captures/references.png) |
| C: limited observations | compact_a / s6_09 | Explicit unavailable means; zero-click versus ineligible periods; compiler context is identified. This historical agent output was repaired. | [Expanded](artifacts/presentation_v1/gallery/observations/index.html), [compact](artifacts/presentation_v1/gallery/observations/figure.html), [PNG](artifacts/presentation_v1/captures/observations.png), [status SVG](artifacts/presentation_v1/gallery/observations/charts/focus-observations.svg) |
| D: assessment activity | compact_a / s6_17 | Weekly submission measures and dated record states; grade/learning limitations stay visible. | [Expanded](artifacts/presentation_v1/gallery/assessments/index.html), [compact](artifacts/presentation_v1/gallery/assessments/figure.html), [PNG](artifacts/presentation_v1/captures/assessments.png), [assessment SVG](artifacts/presentation_v1/gallery/assessments/charts/focus-assessments.svg) |
| E: preserved incomplete answer | compact_a / s6_15 and baseline / s6_15 | Same question; earlier peer answers remain earlier; a personal insufficiency does not create the omitted recent peer answer. | [Agent](artifacts/presentation_v1/gallery/incomplete/index.html), [baseline](artifacts/presentation_v1/gallery/baseline/index.html), [agent PNG](artifacts/presentation_v1/captures/incomplete.png), [baseline PNG](artifacts/presentation_v1/captures/baseline.png) |

All original claims, values, windows, distinct references, panels, conclusions,
caveats and multiplicities remain accessible. Compact views are labeled excerpts,
with the complete content and original dashboard links below them. The renderer
never reads evaluator requirements or unselected tool results. It selects layouts
from semantic content, not case IDs. No missing answer is inserted.

Figure 2 records an actual browser interaction, holding the person, measure,
focal weeks 8–11 and 0–8 display scale fixed. The selected reference changes from
recent presentation peers to presentation peers in weeks 0–3. Values and sample
sizes come from the corresponding saved records. This does not run an agent or
an analytical follow-up. All three saved references are accessible.

Figure S1's external annotations cite the existing Stage 6 audit. The agent's
recent course-peer result was retrieved but not selected as a peer answer. Both
of its selected peer answers use weeks 0–3. The separate baseline explicitly gives
personal and recent-peer insufficiency. The new renderer preserves this failure;
numerical verification is never labeled complete question coverage.

## Verification and limits

| Check | Status and evidence |
| --- | --- |
| Historical and frozen artifacts unchanged | **PASS**: all 7,254 files tracked at the starting commit match the [inventory](artifacts/presentation_v1/historical_inventory.json). |
| Historical source-bound numerical validation and replay | **PASS**: six saved dashboards / 15 evidence bindings; original specs, evidence and selection provenance replay identically. [Results](artifacts/presentation_v1/verification.json). |
| Focused mapping and Stage 6 regressions | **PASS**: 25 checks in the combined run; 13 presentation checks rerun after the final content changes. [Test record](artifacts/presentation_v1/checks.json). |
| Browser behavior and displayed content | **PASS**: both routes for six cases; evidence links, original claims, values/units/windows/counts/intervals, SVG bounds and saved-reference state checked. [Browser verification](artifacts/presentation_v1/inspection/browser_verification.json). |
| Capture provenance and controls | **PASS**: 15 captures, all three saved reference states, fixed focal window/value/scale, no browser errors or external requests. [Capture manifest](artifacts/presentation_v1/capture_manifest.json). |
| Paper-size and visual inspection | **PASS for preferred candidates**: all five candidate/proof pages opened in Chromium; the four-panel reduction is explicitly rejected. [Inspection notes](docs/presentation_v1/INSPECTION.md). |
| Clean regeneration | **PASS**: all 31 checked exports are byte-identical across fresh output roots: 16 individual/responsive PNGs and 15 composite PNG/PDF/proof files. [Results](artifacts/presentation_v1/reproducibility.json). |

Peer intervals remain peer-mean bootstrap intervals, not prediction intervals or
contrast uncertainty. Personal changes have no interval. Administrative eligibility,
zero recorded clicks, unknown logging completeness and unavailable measurements
remain distinct. Dated assessment snapshots are not achievement scores or an
updated obligation/grade record. Reference membership can change across periods.

The [Stage 6 scoring caveat](docs/stage6/SCORING_CAVEAT.md) is unchanged. No evaluator
or experimental success rate was revised. Human scientific review remains pending;
this implementation and Codex visual inspection are not independent human review.
Readability was checked in browser/PDF-size proofs, not a physical print or user
study. No manuscript template was available, so actual venue dimensions still
need confirmation. There is no inference of improved accuracy or usability.

## Reproduce

```bash
# Preview; then open the gallery URL below. Ctrl-C stops this optional server.
python3 -m http.server 8765 --bind 127.0.0.1 --directory .

# Regenerate the presentation and figure package.
.venv/bin/python scripts/presentation_v1/build.py
.venv/bin/python scripts/presentation_v1/capture.py --chromium /snap/bin/chromium
python3 scripts/presentation_v1/compose.py
.venv/bin/python scripts/presentation_v1/browser_review.py --chromium /snap/bin/chromium

# Verify the changed boundaries and historical replay.
.venv/bin/python -m pytest -q tests/presentation_v1 tests/test_stage6.py
.venv/bin/python scripts/presentation_v1/verify.py --replay
```

Gallery: <http://127.0.0.1:8765/artifacts/presentation_v1/gallery/index.html>.
The pages also work as local files. Dependencies, clean-output reproduction,
capture dimensions, fonts and raster/vector distinctions are documented in
[REPRODUCTION.md](docs/presentation_v1/REPRODUCTION.md).

No model inference or GPU computation was started. Chromium used `--disable-gpu`. Reserved observations were not
opened. Only CPU verification and local browser rendering were used. Browser
processes were closed, no preview server was left running, and the pod was not
contacted or changed. [Run metadata](artifacts/presentation_v1/run_metadata.json)
records the bounded presentation work. Stop here; no subsequent research stage
or final evaluation was begun.

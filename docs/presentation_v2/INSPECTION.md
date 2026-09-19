# Browser and paper-size inspection

Inspected on 19 September 2026 using Chromium 153.0.8010.36 with GPU rendering
disabled. This was implementation and assisted visual inspection, not independent
human scientific review or a usability study.

Before implementation, the actual saved specifications, evidence and bound claims
were read for all four requested compact-A examples and the s6_15 failure. The
previous browser views and original failure dashboard were opened and captured;
see `artifacts/presentation_v2/prior_inspection.json` and `before_*.png`.
The official-template dimensions were read from the verified archived manifest.

## What was inspected and changed

| View / figure | Inspection outcome |
| --- | --- |
| Personal | Separate personal change and selected peer cards; recent selected peer answer now appears first in the expanded view. Earlier/recent shading and peer-mean band remain. Correct unrounded change −10.54 is preserved with its rounding explanation. The duplicate personal claim retains both source indices. |
| References | All three selected comparisons share the same focal value/window/scale. Actual selector, result/chart replacement, evidence link, permalink/reload and invalid-ID recovery work. Mobile control names were shortened after a clipped-label inspection finding; exact windows and definitions remain in the card and chart. |
| Observations | Zero-click blocks, hatched ineligible blocks and unavailable recent quantities remain distinct. Original compiler attribution and historical repair status are visible. Dated assessment context remains in the expanded view; no unavailable value becomes zero. |
| Assessments | Measures keep their units and denominators; dated records retain their as-of days. The day-55 no-submission snapshot is not updated to day 83. Grade/approval uncertainty remains a measurement limitation, not a sample-size or achievement claim. |
| Incomplete / enumeration | The agent keeps two earlier peer claims and separate personal insufficiency; enumeration alone has the explicit recent-peer insufficiency. The agent's missing answer was not inserted. External S1 annotation identifies weeks 10–11 versus 0–3. |
| Figure 1 | Personal/observation pair is readable at 158.0134 mm; minimum critical text 8.50 pt. No overlap or clipping observed. |
| Figure 2 | Two actual saved-reference states, 104.2 mm tall; minimum critical text 8.80 pt. Fixed person/metric/window/scale and changed reference windows/counts are explicit. |
| Figure S1 | Faithful excerpts with outside editorial notes; minimum critical text 8.54 pt. The baseline's recent insufficiency and agent's omission remain different. |
| Figure S2 | Reference/assessment pair; minimum critical text 8.27 pt. Snapshot dates, unavailable grades and interval meaning are legible. |
| Four-panel trial | Fits 235 mm height only at about 5.17 pt critical text. Retained as a rejected reduction trial; the readable paired alternatives are recommended. |
| Official-template proof | All four A4 pages inspected individually at the intended CSS reading size, plus 96/150 dpi exports. Normal margins and 9 pt captions fit; no oversized floats, clipped text or overlapping labels. |

Desktop (1280 px), mobile (390 px), and 500-pixel publication surfaces were captured.
The final browser pass opened all twelve routes, five figure proof pages, the
gallery, and all four official-template pages. Evidence links and expanders were
exercised. Browser errors, external requests and broken local links were zero.
All owned browsers were closed and no server was started.

The first automated capture check incorrectly expected the assessment denominator
inside each feature card; the check now verifies the explicit common denominator
and agreement of both underlying records. A second check tried a selector on the
support-limited view because its underlying peer records were technically compatible;
the view intentionally has no selector. That check now follows the semantic layout.
The retained `capture_attempt_02.txt` documents the latter harness timeout. Neither
change relaxed evidence, units, window or support checks. A composition command
issued before the capture manifest existed was retried after capture completion.
These were production/check sequencing issues, not experimental reruns.

## Verification evidence

- `checks/tests.txt`: **22 focused tests pass**, including inherited mapping,
  zero/missing distinction, duplicate multiplicity, selection-only controls,
  preserved wrong-window omission, and visible historical repair attribution.
- `checks/verification.json`: **7,799 initial tracked files unchanged**; six
  dashboards / 15 saved evidence bindings replay through the original source-bound
  numerical validator; no analytical dispatcher call or scoring run.
- `capture_manifest.json`: 23 high-resolution captures and all saved reference
  states; DOM values/intervals/counts and SVG metadata agree with saved records.
- `checks/browser_review.json`: final controls, links and physical-size proofs.
- `checks/reproduction.json`: **103/103 exports byte-identical** in a fresh build
  (individual PNGs, 56 native SVGs, composite PDFs/PNGs, proof PDF and pages).
- `proof/compile_2.txt`, `proof/fonts.txt`: successful official-template compilation
  with embedded fonts, no overfull boxes or oversized floats.

Limits: CSS millimetres and screen inspection are not a calibrated print; a final
100% physical proof is still useful before publication. Dense original-context
charts are smaller in the mobile expanded view; readable publication excerpts
and standalone SVGs remain accessible. Full originals govern scientific review,
not the excerpted figures. Scoring caveats and human scientific review remain
pending. Presentation quality supplies no new accuracy, usability or generalization
evidence, and the manuscript remains unchanged.

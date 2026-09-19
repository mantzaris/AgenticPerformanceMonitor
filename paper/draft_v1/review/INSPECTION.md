# Draft V1 inspection record

Inspected 19 September 2026. This is assisted editorial and implementation
inspection, **not independent human scientific review**. No reviewer form was
filled and no experimental judgment or score was changed.

The inspected final PDF has SHA256
`0065edd8e58fab37675156f02e7a9daee64caf62321cd793dc904b25ac8143a8`.
All 12 pages were rendered with Poppler at 96 and 150 dpi. Chromium 153.0.8010.36
loaded every 96-dpi page at 210 mm CSS width (794 pixels at 96 dpi), in an
850×1200 viewport with device scale 1 and GPU rendering disabled. Every page was
also visually inspected individually. CSS physical units and a screen inspection
are not a calibrated printed proof or a usability study.

| Page | Inspected content and outcome |
| --- | --- |
| 1 | Anonymous title, 188-token abstract, keywords, introduction and disclosure footnote. No author block, clipping or unresolved macros. Abstract matches frozen table counts and acknowledges disputed scoring. |
| 2 | Related work and data introduction. Citations resolve; long author lists wrap. Prior missing-task/attribute-binding work is acknowledged, without claiming the general distinction is new. |
| 3 | Eligibility, zero/unavailable distinctions, five measures, repeated rows, weighting equations and bootstrap procedure. Equations fit the columns; source rows are not confused with distinct people. |
| 4 | Evidence identities, personal-versus-peer scope, validation, compiler contributions and later presentation. No overlapping equations or body text; compiler context is distinguished from method selections. |
| 5 | Architecture at full text width, caption and experimental design. Diagram labels remain at least 8 pt; arrows distinguish requests, returned results, validation, repair and saved-record presentation. |
| 6 | Personal/observation figure at full width. Recorded zero and ineligibility differ in text and hatching; unavailable values are explicit. Peer-mean interval, rounding note, compiler attribution and historical repair remain visible. Minimum critical text is 8.50 pt. |
| 7 | Conditions, all five window profiles, runtime, endpoints and start of results. Pin fits the column. B–A is explicitly an interface package; selected completeness is not model arithmetic. |
| 8 | Generated outcome table, frozen results figure and paired table. All four conditions and 24-case denominators are visible; mutually exclusive categories sum to 24. B17–20 caveat appears beside the chart. Minimum chart text is 8.5 pt. |
| 9 | Failure mechanisms, dedicated answer-equivalence caveat, process costs and interpretation. B17–20/C21/C23 remain unresolved. No score revision or claim of human adjudication. |
| 10 | Reference-switch figure, generated cost table and assessment example. Fixed focal value/scale and changed reference window/sample sizes are explicit. Intervals remain peer-mean intervals. Minimum figure text is 8.80 pt; table fits text width. |
| 11 | Failure figure, limitations and conclusion. Editorial annotations remain outside faithful captures; earlier peer answers do not become recent answers. Missing recent peer answer and separate personal insufficiency survive. Minimum figure text is 8.54 pt. |
| 12 | End of conclusion, nonidentifying AI-use disclosure and 15 references. No hidden author/repository identification, missing citation, clipped DOI or placeholder. Bibliography remains within normal margins. |

Layout was revised after inspection: long queued floats were placed using normal
top-of-page placement; repeated prose was shortened; the standalone assessment
capture was retained as an unused review candidate rather than shrinking six
large figures into the paper. The substantive assessment description remains in
the main text. A short-window profile omitted from an earlier draft was restored
from the task manifest, and an awkward split at a figure boundary was reworded.
The official style, geometry, caption formatting and body fonts were not changed.

## Checks and reproducibility

- [`verification.json`](../checks/verification.json): all 7,711 initial tracked
  files unchanged; 96 frozen slots retained; four copied UI PDF content streams
  unchanged; all reviewer fields blank; official template files byte-identical.
- [`reproducibility.json`](../checks/reproducibility.json): a full second build
  produced identical bytes for the PDF, all ten publication figure files, and
  four generated LaTeX tables/macros (15 outputs total).
- [`browser.json`](../checks/browser.json): all pages loaded; both saved-reference
  states exercised for text/count inspection; no browser errors or external
  requests; owned browser closed. No local server was needed.
- [`character_count.json`](../checks/character_count.json): 37,958 extracted
  non-whitespace characters plus 2,391 raster-panel characters = **40,349**.
  With a separately reported conservative glyph allowance of 500: **40,849**.
  This is a reproducible estimate, not the venue's submission counter.
- [`latex_3.txt`](../checks/latex_3.txt) and [`bibtex.txt`](../checks/bibtex.txt):
  no overfull boxes, undefined references/citations, missing glyphs or LaTeX
  warnings. Remaining underfull justification notices were visually inspected;
  no clipped or overlapping text was found. All fonts are embedded, as recorded
  in [`pdffonts.txt`](../checks/pdffonts.txt).

The main PDF is self-contained; internal provenance and review links are kept
outside it. Source-bound consistency and page inspection cannot resolve the
pending scientific decisions in
[`DECISIONS_BEFORE_SUBMISSION.md`](../DECISIONS_BEFORE_SUBMISSION.md).

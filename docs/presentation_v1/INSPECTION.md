# Browser and figure inspection

The original six saved pages were opened in Chromium before design. Their captures
and browser record are under
[`inspection/original/`](../../artifacts/presentation_v1/inspection/original/).
The long original claim lists, repeated panels and absent focal bars motivated a
separate compact presentation; none of those historical files was changed.

The expanded new views were first inspected at a 1000 CSS-pixel viewport. They
retain useful interactive detail but are too tall and dense to shrink as whole
pages into paper panels. A compact reading route was then implemented using the
same selected content. It is explicitly labeled an excerpt and retains the full
original content below its captured surface. The final paper figures use these
actual compact browser views, not reconstructed screenshot illustrations.

The compact route increased chart-label sizes and critical body text to 18 CSS
pixels. The initial 2 × 2 composition was fitted to 180 × 240 mm and inspected as
a 96 dpi proof. The resulting approximately 5.4 pt text was too small. Figure 1
now uses personal and reference panels; Figure S2 carries the observation and
assessment panels. At their assumed widths, critical text is approximately 8 pt.
The four-panel reduction proof remains as a rejected candidate, not an endorsed
publication figure.

## Inspected final artifacts

Codex inspected the expanded and compact screenshots, every preferred figure,
the supplementary failure pair, the rejected four-panel proof and the local
gallery. Chromium opened all twelve reading pages and all five figure proof
pages, including each full-resolution image control. The browser captures of
those proofs are under
[`inspection/`](../../artifacts/presentation_v1/inspection/).

| Output | What was checked |
| --- | --- |
| Figure 1(a), Case A | Earlier/recent labels, 14.07 → 3.54 and −10.54 personal change, four observations per window, selected recent peer mean 4.22 and difference −0.68. Shaded periods are distinct from the peer CI band. The earlier peer answer remains available below the excerpt. |
| Figure 1(b), Case B | Same 3.50 focal value in all three rows; visible reference-period labels; point/whisker shape cues; common 0–8 scale; selected card matches the highlighted row. |
| Figure 2 | Browser changed the selected reference through all three saved options. Person/window/scale remained fixed. Displayed means, difference, counts, intervals and evidence target moved together. Course and earlier-period states were captured after real select events. No request to an analysis service occurred. |
| Figure S2(c), Case C | Four earlier zero-click weeks versus four recent ineligible weeks; no null value shown as zero. All three unavailable measurements are named. Original compiler provenance for observation/grade context is visible. No effort inference. |
| Figure S2(d), Case D | Means 0.25 and 0.00 per observed week, peer values and intervals, four focal weeks, dated states as of days 20 and 55. These states are not represented as grades or as recent-window events. |
| Figure S1, Case E | Personal insufficiency is explicit in both pages. The agent retains two earlier peer answers and no new recent peer answer. The baseline gives the separate recent peer insufficiency. Different earlier-peer CI endpoints remain distinct. Editorial failure commentary is outside the captures. |
| Expanded pages | All original claims, multiplicities, conclusions, panels, technical source IDs, context and SVG downloads are accessible through working expanders/links. |
| Narrow view / gallery | No horizontal overflow in the 600-pixel reading view. Gallery previews were changed to contain the whole preview instead of clipping metric text. |

The browser audit checks visible/expandable card text against saved units, windows,
means, differences, counts and interval endpoints. Every SVG text bounding box is
checked against its native viewbox after expanding the original panels. No clipped
SVG labels, broken case-page links, page exceptions or external requests remained.
The visual review found no overlapping labels or misleading scale change in the
preferred figures. No print on physical paper, color-vision study, usability test
or independent human scientific review occurred.

Mechanical capture failures occurred during development: a URL fragment was
mistakenly treated as part of a filename, and a newly named `inspect.py` shadowed
Python's standard module. Both were fixed before final capture; the latter script
is now `browser_review.py`. Clean regeneration also exposed Snap Chromium's
inaccessible host `/tmp` and path-dependent PDF image identifiers. Reproduction
now uses an accessible fresh repository directory, and PDF image identifiers
derive from image content. All 31 checked exports are byte-identical across
output roots. No failure changed saved evidence or experimental outputs. A
[machine record](../../artifacts/presentation_v1/checks.json) retains these resolved
issues separately from the final passing checks.

All screenshots and figure manifests record source hashes, browser version,
viewport, scale factor, selector, crop bounds and reference state. Exact image/PDF
regeneration is checked separately; numerical validity is never equated with
answer completeness.

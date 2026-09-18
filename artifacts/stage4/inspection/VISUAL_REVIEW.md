# Stage 4 visual inspection

Selection was frozen before inference: the first case in each family (01, 03,
05, 07, 09, 11), for all three methods, including failures. Chromium 153.0.8010.36
opened all 13 accepted exports among those 18 slots, exercised the provenance
inspector and checked visible claims/conclusions against bound records. Five slots
have no accepted dashboard; they were not replaced. See [browser.json](browser.json).
No browser errors occurred. Self-contained file URLs required no local server;
the browser was closed after capture.

Codex additionally inspected the following seven screenshots. This is automated
verification and agent visual review, not independent human scientific/usability
review. Numerical source validation and exact replay cover every accepted output,
not just these representatives.

| Family / selected export | Visible result and inspection |
| --- | --- |
| Personal change: [compact 01](semantic_s4_01.browser.png) | Personal 15.61 to 1.79, change -13.82; recent course mean 4.13, difference -2.34, 228 peers / 905 person-weeks. Explicitly selected earlier-stage comparison is additional context, not extra credit. Zero-activity weeks and reference-mean interval labels are visible. |
| Reference comparison: [compact 03](semantic_s4_03.browser.png) | Focal 0.71; course 3.46, prior-attempt 2.41, earlier-stage 6.95. Differences have the same sign. All three definitions/counts are visible; no claim of a fairer causal reference. |
| Observation limitations: [baseline 05](baseline_s4_05.browser.png) | Recent focal clicks 0.07 with two eligible observed weeks; submissions and scheduled non-submissions are 0.00. The observation strip distinguishes recorded activity, zero recorded activity and ineligibility. Unknown logging is a caveat, not a fabricated logging-failure diagnosis. |
| Insufficient support: [baseline 07](baseline_s4_07.browser.png) | Peer comparison and personal change each receive a scoped insufficiency statement. Earlier history has one observed week and recent history none. The peer mean remains visible but is not presented as an individual estimate. |
| Insufficient support: [full 07](full_spec_s4_07.browser.png) | Accepted but incomplete: four repeated personal-insufficiency claims and trajectories do not answer the requested peer comparison. The broad concluding insufficiency statement does not rescue that omission. |
| Assessment availability: [compact 09](semantic_s4_09.browser.png) | Accepted but incomplete: nonbanked submissions are 0.00, but the requested scheduled-no-submission weekly comparison is absent. Extra personal/peer comparisons do not replace it. Compiler-supplied assessment states and grade-release caveat have separate attribution. |
| Alternate windows: [compact 11](semantic_s4_11.browser.png) | Focal 4.18; course and same-prior-attempt 7.33, earlier-stage 13.05; personal 1.07 to 4.18. All requested contrasts are shown, with the same peer-comparison direction. Three identical personal-change claims/trajectories are explicitly selected through different evidence IDs and clutter the page. |

All inspected visible numerical statements match bound evidence. The shared
renderer labels bootstrap bands/whiskers as uncertainty for peer means, not
individual prediction intervals; personal changes have no interval. Source rows
and measurements retain the earlier statistical limitations.

Remaining presentation defects: long questions and dense reference definitions
produce tall pages; repeated selected claims/panels can obscure otherwise complete
answers; zero-height bars are visually absent although numerical text reports
zero. Assessment-state points use scheduled due-day positions and recorded
week-end states; richer as-of metadata is in the evidence inspector, not the chart
title. These limitations were recorded without changing the frozen renderer or
scoring. Only one desktop browser was checked. No usability study was performed.

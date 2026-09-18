# Representative browser and visual review

Selection followed the frozen rule: first case in personal change, reference
sensitivity, assessment availability and insufficient support, phrasing a;
baseline and proposed policy when accepted. Failed proposed outputs were retained,
not replaced with better examples. See [browser.json](browser.json) for the actual
Chromium version, rendered text assertions, screenshots and form interaction.
This was automated browser inspection plus Codex image inspection, **not independent
human scientific or usability review**. One desktop browser was used.

| Example | Observation and limitation |
|---|---|
| `coverage_aware/s3_01a` | The personal change 2.79 to 0.25 is correctly displayed. The recent course comparison is missing, while baseline-course and earlier-stage comparisons occupy space. The scorer marks this valid dashboard incomplete. Several substantively overlapping panels make it long even without identical panel signatures. |
| `baseline/s3_03a` | The three recent focal/reference contrasts are negative (-2.31, -5.78, -1.29 recorded clicks per eligible day); the same-direction conclusion is supported. Personal history is extra material and earns no answer credit. Counts, reference windows and peer-mean interval labels are visible; long labels are dense. The proposed output failed validation and has no accepted dashboard. |
| `baseline/s3_09a` | Non-banked submissions 0.25/week and scheduled assessments without submission 0.00/week are shown with the unavailable-grade/learning caveat. Assessment states concern the due week's end (`as_of_day` 20 and 55), not the final cutoff; the due-day chart can be misread as a current status without inspecting that metadata. A later submission can coexist with an earlier non-submission state. Zero-height bars are visually unobtrusive, but numeric claims show zero explicitly. The proposed output failed validation. |
| `coverage_aware/s3_07a` | The displayed earlier-window comparison (14.57 versus 7.26) is source-supported, but does not answer the requested recent or personal comparison. Grey ineligible weeks are visible. Neither requested insufficiency is scoped in the answer; the scorer correctly gives no requested-answer coverage. |

The baseline counterparts render and expose the same controlled quantities,
definitions and evidence inspector. Displayed accepted numerical conclusions
match their selected evidence; this is not a claim that every accepted dashboard
answers its user's question. Boilerplate and extra panels can obscure omissions.
No renderer or policy was changed after seeing pilot results.

## Follow-up interaction

The actual browser form on baseline `s3_07a` changed reference from `course` to
`early_stage` and profile from `short` to `standard`. The new cutoff is day 83,
baseline weeks 0–3 and recent weeks 8–11, compared with the parent's day 27 and
weeks 0–1/2–3. New analytical evidence, specification and exports were saved at
[the linked child](../followups/s3_07a_followup_0171394851/dashboard.html). Parent
hashes remain unchanged. The evidence inspector opens.

The child visibly states both unsupported comparisons: zero recent observed focal
weeks and two earlier observed weeks. No apparent improvement was manufactured.
The peer mean remains available (6.9260; peer-mean bootstrap interval
6.3792–7.5018); it is not an individual prediction. The child's heading and reference
label show the new settings. The reference form itself defaults back to `course`,
so its selected option does not reflect the currently displayed `early_stage`
result; this existing UI limitation is recorded without post-pilot repair.

Saved images: [before](followup_before.browser.png),
[after](followup_after.browser.png), [inspector](followup_inspector.browser.png).
The follow-up server was stopped after inspection; no model call was required.

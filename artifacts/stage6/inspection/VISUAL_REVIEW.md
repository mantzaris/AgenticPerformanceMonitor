# Stage 6 display and trace inspection

The frozen rule selected the first case in each of six families for all four
conditions, plus the first valid-incomplete and rejected output per agent when
needed. Chromium 153.0.8010.36 inspected 28 slots: 26 accepted pages rendered,
two rejected slots retained without replacement. Bound claims and conclusions
were found in the page, SVG panels loaded, and the provenance expander worked.
There were no browser errors. The browser closed; no local server was started.
See [browser records](browser.json) and the [pending human packet](../human_review/README.md).

Codex visually inspected these eleven screenshots; this is not independent human
scientific or usability review.

| Screenshot | Observed result and limitation |
| --- | --- |
| [C01](binding_c_s6_01.browser.png) | Personal click rate 14.07 to 3.54; change −10.54. Recent course peer mean 4.22 and difference −0.68. Both requested answers are explicit; an optional earlier peer answer also appears. |
| [C05](binding_c_s6_05.browser.png) | Recent rate 3.50 versus course 3.46, prior-attempt 2.43 and earlier-stage 6.98. All three scoped comparisons appear. Neutral heading adds no cross-reference conclusion; the frozen equivalent-answer rule credits the complete comparisons. |
| [C09](binding_c_s6_09.browser.png) | No recent focal observations; recent means are unavailable, not zero. Earlier zero activity is yellow and later ineligibility gray. Assessment/observation and grade context are compiler supplied, so visible completeness is not model-selected completeness. |
| [C13](binding_c_s6_13.browser.png) | Peer and personal insufficiency are separately explicit. One earlier and zero recent focal weeks; peer pool 1,105 people/2,203 person-weeks. |
| [C17](binding_c_s6_17.browser.png) | Recent submissions 0.25/week and scheduled non-submissions 0.00/week appear in comparison claims. Assessment states are selected; grade limitations are shared context. Earlier-window panels and status panels repeat. |
| [C21](binding_c_s6_21.browser.png) | All recent peer comparisons are present, with extra earlier comparisons. No explicit personal-change answer was selected or inserted. The scorer marks personal change omitted; human review should consider the displayed earlier/recent focal means as a possible alternative form. |
| [B17](derived_b_s6_17.browser.png) | The personal-change claims explicitly state both requested recent assessment means (0.25 and 0.00/week), despite frozen focal-item scoring marking them omitted. This triggered the separately documented scoring caveat. Panels repeat. |
| [B09](derived_b_s6_09.browser.png) | Three repeated general measurement caveats and trajectories appear; the requested window means/explicit unavailability answers are absent under the frozen rule. General limitations do not identify every missing comparison. |
| [A15](compact_a_s6_15.browser.png) | Earlier course and earlier-stage answers and repeated personal insufficiency are visible. The requested recent course-peer answer is missing despite retrieval. |
| [Enumeration 13](baseline_s6_13.browser.png) | Both requested insufficiencies are explicit, with windows and support counts; short and complete. |
| [C12](binding_c_s6_12.browser.png) | Click-rate answer uses weeks 0–3 (27.21), while the question asks weeks 8–11. The label itself is honest; the recent answer is omitted. The binding is valid but does not establish question coverage. |

All displayed intervals are reference-mean bootstrap intervals, not prediction
intervals. Personal changes have no uncertainty interval. Numerical means, windows,
reference labels and denominators match source-bound results. An unavailable focal
bar disappears rather than showing a dedicated marker; the claims/status panels
carry the interpretation. Repeated panels and caveats can obscure the requested
answer. Existing presentation limitations were preserved during the experiment.

Original traces were also inspected for A12 (peer selections/personal conclusion
scope, rejected after repair), A22 (unreturned ID then invalid descriptive scope),
B23 (common panel limit, repaired), and C18–20 (invalid analysis batches, zero
returned evidence, invented unresolved handles, rejected after repair). C18–20
never received a returned catalogue; their failures cannot be attributed to
catalogue contents alone. Every comparison generation reached EOS, with at most
491 output tokens, so these observed failures are not output truncation.

All 91 accepted comparison dashboards replay exactly; all 67 accepted agent
specifications and provenance records recompile from saved tool results. No
compiler-added comparison or personal-change claim was found. See
[verification](../checks/final_verification.json) and
[scoring caveat](../../../docs/stage6/SCORING_CAVEAT.md).

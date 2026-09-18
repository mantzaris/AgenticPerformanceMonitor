# Stage 5 display and trace inspection

Inspection used the frozen first-case-per-family rule plus the first valid-incomplete
and rejected case per agent condition. [Browser records](browser.json) retain all
31 selected condition/case slots: 23 rendered, eight rejected with no substituted
dashboard. Chromium 153.0.8010.36 opened self-contained files, checked every bound
claim and conclusion in the page, found SVG panels, and exercised the provenance
expander. There were no browser errors. No server was started.

Codex visually inspected these ten screenshots, covering all six families and all
five conditions. This is automated/Codex review, not independent human review.

| Screenshot | Observed content and limitation |
| --- | --- |
| [14B compact 01](qwen14b_semantic_s5_01.browser.png) | Personal click rate 17.39 to 2.64, change -14.75; recent peer mean 4.16 and difference -1.51. Both requested answers reach the visible claims. Personal claims and trajectories repeat for baseline/recent evidence IDs. |
| [14B compact 03](qwen14b_semantic_s5_03.browser.png) | Recent focal rate 0.00; course, prior-attempt and earlier-stage peer means 3.46, 2.43 and 6.96. All three comparisons are visible. Zero bars have no length, but numerical claims disambiguate zero from unavailable. The descriptive conclusion is acceptable under the frozen equivalent-answer rule. |
| [14B compact 05](qwen14b_semantic_s5_05.browser.png) | Zero observed focal weeks in the recent window; all three requested measurements are unavailable rather than zero. Gray ineligibility is distinct from earlier yellow zero activity. The compiler supplies the dated assessment-state panel, so this is visibly complete but not completely method-selected. Observation panels repeat. |
| [14B compact 07](qwen14b_semantic_s5_07.browser.png) | Personal insufficiency is explicit. Displayed peer answers use the baseline course window and the earlier-stage reference; the requested recent course-peer answer is absent. The page is valid but incomplete. Repeated personal claims and trajectories make it longer without answering that omission. |
| [14B compact 09](qwen14b_semantic_s5_09.browser.png) | Recent nonbanked submissions 0.25/week and scheduled non-submissions 0.00/week are visible. Dated assessment states and withheld-grade/learning limitations are explicitly selected. Assessment/status panels and caveats repeat. Zero estimates are stated in text despite empty zero-length bars. |
| [14B compact 11](qwen14b_semantic_s5_11.browser.png) | Windows 0–3 and 4–7 are explicit. Personal change 18.14 to 7.07 and all three peer comparisons appear; the earlier-stage mean 13.06 differs from the recent course/prior-attempt mean 7.35. No causal or significance claim appears. |
| [Enumeration 07](baseline_s5_07.browser.png) | Both requested insufficiencies are separately stated with windows and support counts. It is shorter and complete. |
| [14B full 07](qwen14b_full_spec_s5_07.browser.png) | Recent peer insufficiency appears, but personal insufficiency does not. The existential global insufficiency conclusion cannot identify the omitted personal answer. |
| [7B full 07](qwen7b_full_spec_s5_07.browser.png) | Personal insufficiency appears; recent prior-attempt and earlier course comparisons do not answer the requested recent course-peer comparison. |
| [7B compact 01](qwen7b_semantic_s5_01.browser.png) | Personal change and an optional active-days trajectory appear. The recent click-rate peer mean comparison is omitted despite available evidence; the compiler does not fill it in. |

All displayed peer intervals are labeled bootstrap intervals for reference means,
not individual prediction intervals. Personal changes explicitly have no uncertainty
interval. Units, windows, distinct people and person-week counts are visible.
Evidence and selection-provenance links are present. Some text is dense, several
pages repeat equivalent plots, and an unavailable focal bar disappears instead of
showing an explicit marker; the insufficiency claims provide the interpretation.
These are existing presentation limitations, preserved during the controlled
comparison. No claim of general usability is made.

The rejected 14B compact case 06 was inspected through its original
[sequence](../comparison/qwen14b_semantic/s5_06/sequence.json): peer-insufficiency
answers are paired with a personal-scope conclusion, both before and after the
single repair. The rejection is appropriate. Full-interface rejections 05/09/10
retain missing panel-contract errors. No screenshot was invented for a rejected
output, and no enumeration output was substituted.

The independent source-bound replay check covers all 46 accepted dashboards, not
only these screenshots; all 18 accepted semantic specifications and provenance
records recompile identically. See [verification](../checks/final_verification.json).

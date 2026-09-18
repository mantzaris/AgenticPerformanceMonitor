# Time, observation and analytical semantics

The creator-supplied `OULAD.names` is included in the hashed raw archive.
It defines dates relative to presentation start, assessment dates as deadlines,
submission dates as submissions, and banked marks as transferred credit.
UCI encodes missing values using `?`; the adapter explicitly parses both `?`
and empty cells as nulls. No score-release timestamp exists in the archive.

The analysis unit is a person–module–presentation–week. Day 0 is presentation
start; bins are [0,6], …, [77,83]. Queries are as of the end of day 83.
Future activity, submissions and withdrawal dates do not enter the prepared
view. Final outcomes, scores, geographic/demographic fields, and study credits
are never loaded by the feature adapter. Previous module attempts are assumed
to be known at entry; this interpretation needs domain confirmation.

Eligibility begins on registration day. Withdrawal day is the first ineligible
day, an explicit convention rather than verified daily administrative timing.
Future withdrawal values are replaced by null before calculating exposure.
Unknown registration dates produce unknown status and null features, not zeros.
An eligible week without positive clicks has zero recorded activity and unknown
logging completeness. A week with no eligible days is administratively ineligible
and its features are null. Partial weeks retain their eligible-day denominator.
No sensor-coverage claim is made. Post-withdrawal activity records are excluded.

Five features are calculated from independent streams before the weekly join:

| Feature | Definition and availability |
| --- | --- |
| Clicks per eligible day | Sum of all source `sum_click` rows on eligible days, divided by eligible days. Repeated raw rows are preserved, not asserted to be unique events. |
| Active days | Number of eligible dates with at least one positive recorded count. |
| Distinct resources | Number of distinct resource identifiers recorded on eligible dates. |
| Non-banked submissions | Count of dated non-banked submission records on eligible days; scores are discarded. |
| Scheduled without submission | Non-exam deadlines in that week when eligible, with no non-banked submission recorded by that week's end. This is a scheduled-opportunity proxy, not proof of an unmet personal obligation. |

Banked records are excluded from observed submissions. Their grade-release and
approval times are unknown, so they cannot establish an as-of individual exemption.
This can overcount scheduled opportunities for exempt students. Assessment state
records distinguish no recorded submission, recorded non-banked submission,
ineligibility on the deadline, and unknown eligibility. Earlier-week states do not
retroactively incorporate later submissions. Deadlines are assumed available at
entry; the archive lacks schedule revision timestamps. This and registration
availability make the view a conservative retrospective approximation.

Frozen question windows are baseline weeks 0–3 and recent weeks 8–11. Registry:
same presentation, same presentation/prior-attempt group, and course peers in
the earlier stage. References exclude the focal person, use development students
only, and have no outcome-dependent filters. The earlier-stage comparison changes
the estimand; it is not an adjustment that reveals a causal explanation. For each
question all charts also retain the observed same-week temporal context.

Peer summaries first average each person's eligible weekly values, then weight
people equally. Thus a person with one eligible week has the same person-level
weight as one with four; exact counts are exposed. Weekly curves are means among
those eligible that week, with potentially changing composition. Summary intervals
are percentile bootstrap intervals from 500 resamples of people and their intact
within-window histories, using a recorded seed. Weekly intervals resample people
within each week. They are pointwise, descriptive mean intervals, not individual
prediction intervals or simultaneous bands. No multiplicity-adjusted test is made.
At least 20 peers and two observed focal weeks support a comparison; these are
engineering thresholds, not calibrated guarantees. Personal differences are
descriptive and have no uncertainty interval; claims require two observations in
both periods. There is no residual anomaly threshold or personal prediction model.

The separate mixed-model check fits `log1p(clicks / eligible day)` to categorical
week and prior-attempt group (when variable), with a random intercept by person.
It uses development peers, excluding all three focal people, through the cutoff.
REML/L-BFGS has a fixed iteration cap, with warnings and failures retained.
`BBB_2013B` converged; `AAA_2013J` failed with a singular covariance. Descriptive
means serve as the explicitly labeled fallback; there is no hidden alternative
optimizer search. The mixed fit is a statistical feasibility artifact and is not
used to certify the dashboard conclusions. Residual normality, serial independence,
informative withdrawal and model calibration remain unvalidated.

`duplicate_sensitivity.json` compares main summaries with the alternative of
dropping exact repeated source rows, on development data only. Neither alternative
identifies actual unique clicks. More complete statistical validation, dropout
sensitivity and domain interpretation belong to Stage 2.

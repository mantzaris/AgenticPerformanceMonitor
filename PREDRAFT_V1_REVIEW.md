# Pre-draft preparation v1 — review entry point

**Complete as a preparation package. Scientific review remains pending.** Six figure
candidates, a six-page official-template layout proof, a faithful frozen-results
summary, all 96 scientific-review slots and an evidence map/outline are available.
No manuscript, inference, agent tuning, scoring revision or final validation was run.

Starting commit: `321439487ef0035538564f3a2829bab9df859b71`; working tree was clean on
`main`, tracking `origin/main`. Work follows the main-only workflow. Resolve the
handoff commit with `git log -1 --format=%H -- PREDRAFT_V1_REVIEW.md`; the final session
message reports its full SHA and push status. All 7,402 previously tracked files,
including presentation_v1 and frozen experiments, remain byte-identical.

## Open the deliverables

- [Updated local gallery](artifacts/predraft_v1/gallery/index.html), with full saved
  content, evidence inspectors, three working saved references and original links.
- [Official SCITEPRESS layout proof](artifacts/predraft_v1/proof/layout.pdf),
  [browser-readable A4 pages](artifacts/predraft_v1/proof/index.html), and
  [LaTeX source](artifacts/predraft_v1/proof/layout.tex). This is a figure/caption
  proof, not a manuscript draft.
- [All 96 pending review slots and blank forms](artifacts/predraft_v1/human_review/index.html),
  [review guide](docs/predraft_v1/HUMAN_REVIEW_GUIDE.md), and
  [machine-readable packet](artifacts/predraft_v1/human_review/packet.json).
- [Evidence map, proposed outline and decisions](docs/predraft_v1/EVIDENCE_MAP_AND_OUTLINE.md).
- [Captions](docs/predraft_v1/CAPTIONS.md), [semantic/provenance boundaries](docs/predraft_v1/SEMANTICS_AND_PROVENANCE.md),
  [inspection record](docs/predraft_v1/INSPECTION.md), and
  [exact reproduction commands](docs/predraft_v1/REPRODUCTION.md).

| Candidate | PDF | High-resolution PNG | Content |
| --- | --- | --- | --- |
| Figure 1 | [PDF](artifacts/predraft_v1/figures/figure1.pdf) | [PNG](artifacts/predraft_v1/figures/figure1.png) | Personal s6_01 + limited observations s6_09, compact A; compiler timeline attribution and historical repair preserved. |
| Figure 2 | [PDF](artifacts/predraft_v1/figures/figure2.pdf) | [PNG](artifacts/predraft_v1/figures/figure2.png) | Actual s6_05 saved-selector states, recent versus earlier presentation peers; focal quantity/window/scale fixed. |
| Figure 3 | [PDF](artifacts/predraft_v1/figures/figure3.pdf) | [PNG](artifacts/predraft_v1/figures/figure3.png) | Actual agent/tool/binding/compiler/presentation responsibilities; [vector SVG](artifacts/predraft_v1/figures/figure3.svg), [code trace](artifacts/predraft_v1/architecture_trace.json). |
| Figure 4 | [PDF](artifacts/predraft_v1/figures/figure4.pdf) | [PNG](artifacts/predraft_v1/figures/figure4.png) | All frozen Stage 6 outcomes; [vector SVG](artifacts/predraft_v1/figures/figure4.svg), [derived counts](artifacts/predraft_v1/results_categories.json), [per-slot CSV](artifacts/predraft_v1/results_categories.csv). |
| S1 | [PDF](artifacts/predraft_v1/figures/figureS1.pdf) | [PNG](artifacts/predraft_v1/figures/figureS1.png) | s6_15 agent versus enumeration; editorial annotations outside faithful answer excerpts. |
| S2 | [PDF](artifacts/predraft_v1/figures/figureS2.pdf) | [PNG](artifacts/predraft_v1/figures/figureS2.png) | s6_17 assessment measures and dated snapshots, compact A. |

Individual browser captures are in [captures](artifacts/predraft_v1/capture_manifest.json).
Native vector charts are linked from each expanded view and enumerated in the
[source manifest](artifacts/predraft_v1/source_manifest.json). New vector examples: [trajectory](artifacts/predraft_v1/gallery/personal/charts/predraft-trajectory.svg), [observation states](artifacts/predraft_v1/gallery/observations/charts/predraft-observations.svg), [assessment events](artifacts/predraft_v1/gallery/assessments/charts/predraft-assessments.svg). UI figure PDFs contain
raster browser captures with vector editorial labels; they are not vector dashboards.
Architecture/results PDFs and their SVGs are genuine vectors.

## Template and readability

The current [ICAART template page](https://icaart.scitevents.org/Templates.aspx)
links the official [SCITEPRESS archive](https://www.scitepress.org/documents/SCITEPRESS_Conference_Latex.zip),
retrieved 2026-09-19. The [archived template manifest](artifacts/predraft_v1/template/manifest.json)
records SHA256 `ec6cfaa11962e08d5c6a402124f21c3bca3591397521406ab6d1889398a3807a`
and every supplied file hash. The unmodified style specifies **158.0134 mm text
width and 8 mm column separation**, verified again in the compiled proof.

Paired panels are 75.0067 mm wide. Critical UI text is at least 8.50 pt (reference
excerpts 8.80 pt); architecture labels are at least 8 pt, results labels at least
8.5 pt. Captions retain the official 9 pt size. Figure 2 is 98.6 mm tall and S1
114.7 mm, avoiding repeated tall interfaces. No global shrinking or geometry change
was used. All live PDF fonts are embedded. The six A4 proof pages were inspected
at their intended CSS reading size, with 96/150 dpi renders; physical printing at
100% is still recommended before submission. This was screen inspection, not a
usability study or independent scientific review.

## Faithful quantitative summary

Derived directly from the frozen per-case JSON, with every slot retained:

| Condition | Complete via method selections | Additional complete via compiler context | Accepted incomplete | No accepted output | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| Enumeration | 24 | 0 | 0 | 0 | 24 |
| A: compact | 18 | 3 | 1 | 2 | 24 |
| B: derived metadata | 14 | 1 | 9 | 0 | 24 |
| C: explicit binding | 11 | 4 | 6 | 3 | 24 |

“Method selections” denotes deterministic selections for enumeration and model
selections for agents; tools calculate every number. Categories are exclusive and
use the unchanged endpoint. **B17–20 remain in accepted-incomplete**, although their
recent means appear in personal-change claims. The [existing scoring caveat](docs/stage6/SCORING_CAVEAT.md)
requires adjudication, not silent credit. No significance markers, invented
uncertainty, cross-stage trend or revised experimental scores were added.

## Human review and scientific decisions

The packet uses the full original experimental dashboards/questions, including all
five rejections. Seed 20260919 randomizes the 96 slots; neutral condition labels
have a [separate coordinator mapping](artifacts/predraft_v1/human_review/coordinator_private/reconciliation.json).
This is partial masking: original content/paths can reveal condition identity, and
“private” is a workflow separation, not access control. Initial forms contain no
frozen judgments; [automated judgments and separate calculation facts](artifacts/predraft_v1/human_review/audit/automated_judgments.json)
are segregated. Both independent forms and adjudication fields remain blank.
No reviewers were contacted, identities invented or agreement statistics calculated.

Before drafting settled scientific claims, adjudicate B17–20, separately displayed
personal windows including C21, unavailable-answer forms, and separately scoped
peer/personal insufficiency. Review support thresholds, duplicated-source treatment,
weighting and reference appropriateness. A later adjudicated analysis must be
versioned and labeled post hoc, with frozen scores preserved.

The current direction is an audited development study of analytical selection,
numerical checking, compiler attribution and completeness failures. Enumeration
remains the operational baseline within a small predefined registry. No superiority,
unrestricted UI generation, usability improvement or other-domain generalization
is established. An internal engineering gate is not a conference acceptance rule;
missing it does not automatically make a carefully scoped negative study
unpublishable. Novelty, rubric validity and the need for a later fixed validation
study require external scientific decisions. Reserved observations remain closed.

## Verification actually performed

| Check | Result / record |
| --- | --- |
| Changed-boundary and inherited mapping tests | **20 PASS**, [log](artifacts/predraft_v1/checks/tests.txt) |
| Original source-bound validator and six historical replays | **PASS**, [record](artifacts/predraft_v1/checks/historical_replays.json); no `Engine.analyze` call |
| Saved-reference browser interaction | **PASS** all three states; result/chart/window/counts/evidence update together, focal mean/window/scale fixed; [capture manifest](artifacts/predraft_v1/capture_manifest.json) |
| Final views, six figures, six proof pages, full scientific examples, 96 packet pages | **PASS**, zero browser errors, external requests or broken review links; [browser report](artifacts/predraft_v1/checks/browser_review.json) |
| Sources, zero/unavailable/ineligible distinctions, preserved omission, 96 slots, blank forms, result totals, official template, historical files | **PASS**, [verification](artifacts/predraft_v1/checks/verification.json) |
| Fresh-output regeneration | **110/110 exports and forms byte-identical**, [comparison](artifacts/predraft_v1/checks/reproduction.json); temporary replica removed |
| LaTeX and font inspection | Six pages, no overfull boxes or oversized floats; [compile log](artifacts/predraft_v1/proof/compile_2.txt), [embedded fonts](artifacts/predraft_v1/checks/proof_fonts.txt) |
| Independent human scientific review / final validation | **PENDING / NOT RUN** |

[Production metadata](artifacts/predraft_v1/production_manifest.json) records the
starting state, code/font hashes, capture/proof manifests and elapsed snapshot.
Model generations and model-process runtime are **zero**. Browser instances launched
by the scripts are closed; no local server or model process was started, and the
RunPod instance was not accessed or terminated. No new Python dependencies were installed.

```bash
# Preview (Ctrl-C to stop)
python3 -m http.server 8765 --bind 127.0.0.1
# Open /artifacts/predraft_v1/gallery/index.html

# Regenerate and inspect, using the archived official template
python3 scripts/predraft_v1/regenerate.py --inspect

# Focused checks
.venv/bin/python -m pytest -q tests/predraft_v1 tests/presentation_v1
python3 scripts/predraft_v1/verify.py
```

This stage stops at the preparation package. No manuscript or subsequent research
stage has begun.

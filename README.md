# Reference-sensitive longitudinal dashboards

OULAD research prototype. Start with **[STAGE2_REVIEW.md](STAGE2_REVIEW.md)** for
the scientific hardening, frozen development pilot and working local dashboard
follow-up. **[STAGE1_REVIEW.md](STAGE1_REVIEW.md)** remains the unchanged historical
feasibility handoff. The supplied full research plan is preserved; the full
held-out research evaluation has not been started.

Stage 2 reproduction and review commands are in
[docs/stage2/REPRODUCTION.md](docs/stage2/REPRODUCTION.md). Its saved dashboards
replay from a small, hash-checked development feature bundle without raw data,
weights or inference. Start the local follow-up application with:

```bash
.venv/bin/python -m trajectory_dashboards.stage2.followup --port 8765
```

Open `http://127.0.0.1:8765/artifacts/stage2/construction/baseline/c04/accepted/dashboard.html`.
The form executes a new analysis and saves a linked child dashboard. The commands
below describe the historical Stage 1 path; run data regeneration in a fresh
directory to preserve the committed research artifacts.

The system compares a student's recorded activity with course peers, a prior-
attempt subgroup, an earlier study stage and personal history. Deterministic
analytical tools calculate every number. A typed specification selects evidence
and panels; a controlled Altair renderer produces HTML with an evidence inspector
and static SVG/PNG exports. The model cannot supply executable code or numerical
claim values. Statistical support is descriptive, not causal or diagnostic.

Use Python 3.10 (tested locally) or 3.12 (tested on the GPU host):

```bash
python3.10 -m venv .venv
.venv/bin/pip install -r requirements.lock
.venv/bin/pip install -e . --no-deps
.venv/bin/trajectory download
.venv/bin/trajectory prepare
.venv/bin/trajectory analyze
.venv/bin/python scripts/duplicate_sensitivity.py
.venv/bin/pytest -q
.venv/bin/python scripts/verify_artifacts.py
```

Raw OULAD data and prepared bulk tables are ignored by Git. Download verifies the
frozen UCI archive hash. Preparation regenerates the same grouped split and
structurally selected cases. `analyze` intentionally regenerates development
artifacts; preserve the committed reference outputs when comparing a new run.
Timing and source-code provenance may differ; numeric outputs should agree.

Replay needs neither raw data, model weights nor another model call:

```bash
.venv/bin/trajectory replay artifacts/deterministic/dev_1 --output /tmp/apm-replay
.venv/bin/trajectory replay artifacts/gpu/dev_2/accepted --output /tmp/apm-agent-replay
```

Open the resulting `dashboard.html` in a browser. It is self-contained and works
without a server. The charts are static exports; evidence sections expand and
collapse. Follow-up options are suggestions, not interactive analytical execution.

The optional GPU reproduction is documented in the review entry point. It uses
one pinned Qwen2.5-7B-Instruct model and the Transformers backend. Do not run it
to view the existing evidence. The first feasibility run used eight generations;
one case was accepted, one repaired and accepted, and one failed with a separately
labeled deterministic fallback. This is not a measured agent advantage.

OULAD source attribution: Kuzilek, Hlosta and Zdrahal, creator-deposited UCI dataset
[DOI 10.24432/C5KK69](https://doi.org/10.24432/C5KK69), CC BY 4.0. Source observations
are unmodified; derived summaries and dashboards are explicitly identified. Code
uses the repository's MIT license. See [time/statistical semantics](docs/TIME_AND_STATISTICS.md)
and the [focused overlap assessment](docs/LITERATURE_OVERLAP.md).

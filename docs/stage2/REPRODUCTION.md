# Stage 2 reproduction and review

Run from the repository root. Python 3.10 is tested locally and 3.12 on the existing GPU host. Install the same pinned CPU dependencies without downloading weights:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.lock
.venv/bin/pip install -e . --no-deps
mkdir -p data/prepared
cp -n artifacts/stage2/source/weekly.parquet artifacts/stage2/source/assessment_status.parquet data/prepared/
.venv/bin/pytest -q
```

The Stage 2 source bundle is a small **derived, allowlisted development dataset**, copied from the hash-verified Stage 1 preparation. It contains no scores, final results, raw withdrawal dates, reserved trajectories or model weights. It is included so semantic checks and replay work independently of a large raw download. OULAD remains CC BY 4.0; source attribution and archive/file hashes are in the unchanged `artifacts/data/manifest.json`.

## Inspect, score and replay saved results without inference

```bash
.venv/bin/python scripts/stage2/report.py --subset pilot
.venv/bin/python scripts/stage2/audit_insufficiency.py
.venv/bin/python scripts/stage2/verify.py --output /tmp/stage2-verification.json
.venv/bin/python - <<'PY'
from trajectory_dashboards.stage2.backend import Engine
from trajectory_dashboards.stage2.display import replay
replay(Engine(), 'artifacts/stage2/pilot/baseline/p03/accepted', '/tmp/stage2-replay-p03')
PY
```

Choose a new output directory for replay; an existing export is never overwritten. Open `/tmp/stage2-replay-p03/dashboard.html`. `report.py` regenerates only the Stage 2 comparison reports from saved results, including failed tasks. `verify.py` verifies the frozen input hashes, every accepted numerical table against the source bundle, all saved exports, the original Stage 1 inventory and GPU ledgers. It imports no model backend and makes no generation.

## Re-run analysis in a fresh workspace

```bash
.venv/bin/python scripts/stage2/new_workspace.py /tmp/stage2-analysis-reproduction
```

This copies the frozen code, configuration, tasks, rubrics and source bundle to a new directory, leaving historical outputs and ledgers in the original repository. Use the already installed environment by substituting its absolute path below:

```bash
cd /tmp/stage2-analysis-reproduction
PYTHONPATH=src /absolute/path/to/repository/.venv/bin/python scripts/stage2/baseline.py --subset pilot
```

This runs all twelve deterministic analyses and renders their dashboards. It does not call a model. Execution times and timestamps will differ; the bound numerical results should agree. The twelve agent episodes per method are not implicitly repeated.

The original primary reports preserve a frozen insufficiency-scoring defect.
`audit_insufficiency.py` reproduces the separately labeled post-hoc display audit;
it does not change primary scores. Read `reports/INSUFFICIENCY_SCORING_AUDIT.md`
under `artifacts/stage2/` before interpreting that metric.

## Reproduce raw acquisition and preparation separately

Use a new directory because the acquisition/preparation commands intentionally write their own manifests. From the original repository:

```bash
mkdir /tmp/stage2-raw-reproduction
cp -a src configs scripts pyproject.toml requirements.lock /tmp/stage2-raw-reproduction/
cd /tmp/stage2-raw-reproduction
python3 -m venv .venv
.venv/bin/pip install -r requirements.lock
.venv/bin/pip install -e . --no-deps
.venv/bin/trajectory download
.venv/bin/trajectory prepare
.venv/bin/python scripts/stage2/prepare.py
.venv/bin/python scripts/stage2/rubrics.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python scripts/stage2/statistical_checks.py
```

Acquisition verifies the original UCI archive SHA-256. Stage 1 preparation reproduces the person-grouped split and the two presentation feature tables. Stage 2 selection reproduces the same 18 focal people and fixed reference exclusions. Compare feature file hashes, task assignments and numerical results; provenance creation times will differ. Do not replace the committed frozen task/rubric files with a new run. The statistical script checks construction examples only, saves both source-row interpretations and performs one bounded mixed-model diagnostic retry. No full benchmark is included.

## Real local follow-up

```bash
.venv/bin/python -m trajectory_dashboards.stage2.followup --port 8765
```

Open `http://127.0.0.1:8765/artifacts/stage2/construction/baseline/c04/accepted/dashboard.html`.
Select `early_stage` and `short`, then **Analyze and save follow-up**. The server
binds only to loopback, runs the same analytical backend and integrity validator,
and saves a new child under `artifacts/stage2/followups/`. Its `link.json` records
the parent hashes and actual request. The selected primary feature is inherited
from the parent. Profiles jointly specify the time windows and cutoff. A later
cutoff uses only data available at that new cutoff. The original result is not
edited. Stop the server with Ctrl-C.

The saved demonstration is linked from `artifacts/stage2/followup_demo/verification.json`,
with full browser screenshots before and after. To repeat the actual browser
interaction, install the optional client and use an existing Chromium binary:

```bash
.venv/bin/pip install playwright==1.55.0
.venv/bin/python scripts/stage2/browser_followup.py --chromium /path/to/chromium
```

Run this in a fresh reproduction of the relevant construction baseline if you
want to preserve the original demonstration screenshot filenames. The application
itself requires neither Playwright nor a browser download. The automation uses
the documented [browser launch](https://playwright.dev/python/docs/api/class-browsertype)
and [screenshot](https://playwright.dev/python/docs/screenshots) interfaces.

## Optional independent GPU reproduction

Viewing, scoring and replay do **not** need this. A new model run is a new resource
authorization and must use a fresh workspace/ledger. On the already authorized
GPU machine, create a fresh workspace with `new_workspace.py`, then use its frozen
inputs, the existing Stage 1 virtual environment, and the existing downloaded
model directory. Do not provision another pod or download a second model.

```bash
cd /workspace/stage2-independent-reproduction
PYTHONPATH=src /workspace/apm-stage1/.venv/bin/python scripts/stage2/gpu_pilot.py \
  --subset pilot \
  --model-path /workspace/apm-stage1/models/qwen \
  --authorization-start-utc "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
```

The explicit authorization timestamp sets a fresh six-hour deadline in a fresh
ledger without rewriting the historical configuration. It is rejected when that
ledger already contains attempts. The original authorized Stage 2 used the
configuration's fixed deadline and no override. Both methods use the same greedy
decoding and per-episode ceilings. An existing attempted episode is skipped,
including failures. An unclosed process reservation requires manual reconciliation
before restart. File hashes validate the pinned weights; recorded CUDA device
events, GPU placement and process VRAM substantiate GPU execution. The process
exits and releases the model when finished; it never terminates the pod.

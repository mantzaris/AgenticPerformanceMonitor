# Reproduce Stage 3

From the repository root, with the existing `.venv` (or install the frozen
`requirements.lock`, then `pip install -e . --no-deps`). Do not overwrite saved
results or restart a frozen failed episode. The model is unnecessary for replay,
verification, scoring, or follow-ups.

```bash
.venv/bin/python -m pytest -q tests/test_stage3.py
.venv/bin/python scripts/stage3/verify.py --replay --output /tmp/stage3-verification.json
```

Exact saved-dashboard replay to a new directory:

```bash
.venv/bin/python - <<'PY'
from trajectory_dashboards.stage3.core import Engine
from trajectory_dashboards.stage3.display import replay
replay(Engine(), 'artifacts/stage3/pilot/baseline/s3_01a/accepted', '/tmp/stage3-dashboard-replay')
PY
```

Open `/tmp/stage3-dashboard-replay/dashboard.html`. No model call is made.
For an operational follow-up on a saved Stage 3 dashboard:

```bash
.venv/bin/python -m trajectory_dashboards.stage3.followup --port 8766
```

Open `http://127.0.0.1:8766/artifacts/stage3/pilot/baseline/s3_07a/accepted/dashboard.html`,
change the reference/window, and submit. This creates a new saved child and link
under `artifacts/stage3/followups/`; it preserves the parent. Stop the server with
Ctrl-C. The recorded browser exercise is under `artifacts/stage3/inspection/`.

Reproduce task preparation in a **new** workspace from the existing verified
development bundle. The reserved population is not loaded:

```bash
.venv/bin/python scripts/stage3/new_workspace.py /tmp/stage3-preparation --prepare
cd /tmp/stage3-preparation
PYTHONPATH=src /absolute/path/to/repository/.venv/bin/python scripts/stage3/prepare.py
```

The selected people, windows and independent numerical facts reproduce; fresh
execution timestamps/provenance hashes differ. Raw acquisition/preparation remains
documented in the immutable Stage 1 and Stage 2 handoffs. No raw download or model
download is needed for Stage 3.

For a CPU analysis example using the saved Stage 3 pool:

```bash
.venv/bin/python - <<'PY'
from trajectory_dashboards.common import read_json
from trajectory_dashboards.stage3.core import Engine
from trajectory_dashboards.stage2.methods import deterministic
from trajectory_dashboards.stage3.display import render
q = read_json('artifacts/stage3/tasks/manifest.json')['tasks'][0]['question']
engine = Engine()
spec, evidence, requests = deterministic(engine, q)
render(engine, q, spec, evidence, '/tmp/stage3-new-analysis')
PY
```

The frozen scorer is `scripts/stage3/report.py`; it refuses to replace its saved
report. To recalculate, copy the frozen inputs and original `pilot/`, `gpu/` and
`model_ledger.jsonl` into a new workspace, then run it there. Historical reanalysis
uses `scripts/stage3/reanalyze_stage2.py` in a full independent checkout with a
fresh `artifacts/stage3/stage2_reanalysis/` destination; original Stage 2 outputs
are only read. Per-question judgments include original scores and every change.

Optional GPU reproduction requires a new authorized budget and a new workspace.
Do not rerun model episodes in the original artifact directories. On the existing
GPU host, reuse the already downloaded model and Python environment:

```bash
PYTHONPATH=src /workspace/apm-stage1/.venv/bin/python scripts/stage3/new_workspace.py /workspace/stage3-independent-reproduction
cd /workspace/stage3-independent-reproduction
PYTHONPATH=src /workspace/apm-stage1/.venv/bin/python scripts/stage3/baseline.py
PYTHONPATH=src /workspace/apm-stage1/.venv/bin/python scripts/stage3/gpu_pilot.py \
  --subset pilot --model-path /workspace/apm-stage1/models/qwen \
  --authorization-start-utc YOUR_NEW_AUTHORIZATION_START_IN_ISO_UTC
PYTHONPATH=src /workspace/apm-stage1/.venv/bin/python scripts/stage3/report.py
```

The runner verifies all frozen inputs and pinned weight hashes; refuses CPU
fallback; counts setup/profile and every attempted generation; locks an append-only
ledger; checks unclosed process reservations; and enforces the episode, partition,
total-generation, model-process and stage-time ceilings. It preserves failures and
does not repeat any started episode. A new independent reproduction is additional
research, not part of this completed stage's evidence or budget.

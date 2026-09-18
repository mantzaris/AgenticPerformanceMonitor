# Stage 6 reproduction

Use the existing project `.venv` with `requirements.lock`; run from repository root.
Saved outputs require no model weights, raw data, new download or inference.
Choose fresh destinations: result/scoring commands refuse replacement.

```bash
.venv/bin/python -m pytest -q tests/test_stage6.py
.venv/bin/python scripts/stage6/verify.py --replay --output /tmp/stage6-verification.json
.venv/bin/python - <<'PY'
from trajectory_dashboards.stage6.core import Engine
from trajectory_dashboards.stage6.adapter import replay
replay(Engine(), 'artifacts/stage6/comparison/baseline/s6_01/accepted', '/tmp/stage6-replay')
PY
```

Open `/tmp/stage6-replay/dashboard.html`. Every accepted agent output has the same
replay path shape under its condition (`compact_a`, `derived_b`, `binding_c`). The bound result, semantic selection and
compiler provenance remain inspectable. There is no server to start.

Reproduce the new selection and independently calculated facts:

```bash
.venv/bin/python scripts/stage6/new_workspace.py /tmp/stage6-preparation --prepare
cd /tmp/stage6-preparation
PYTHONPATH=src /absolute/path/to/repository/.venv/bin/python scripts/stage6/prepare.py
```

People, questions and numerical facts should match; fresh timestamps/source
manifest provenance will differ. Only development features and split identifiers
are read. To repeat CPU analysis, use the unchanged baseline method:

```bash
.venv/bin/python - <<'PY'
from trajectory_dashboards.common import read_json
from trajectory_dashboards.stage2.methods import deterministic
from trajectory_dashboards.stage6.core import Engine
from trajectory_dashboards.stage6.adapter import render
q = read_json('artifacts/stage6/tasks/manifest.json')['tasks'][0]['question']
engine = Engine()
spec, evidence, requests = deterministic(engine, q)
render(engine, q, spec, evidence, '/tmp/stage6-analysis')
PY
```

For offline rescoring, create a fresh frozen workspace with `new_workspace.py`
(without `--prepare`), copy saved `artifacts/stage6/comparison/`, `gpu/` and
`model_ledger.jsonl` to matching paths, then run `scripts/stage6/report.py` using
`PYTHONPATH=src` and the existing repository Python. The imported scorer is unchanged.

Optional new GPU reproduction requires separate authorization and a fresh budget.
On the same GPU host, create a fresh frozen destination using `new_workspace.py`
(without `--prepare`) and change into it. Reuse the downloaded pinned checkpoint:

```bash
PYTHONPATH=src /workspace/apm-stage1/.venv/bin/python scripts/stage6/baseline.py
PYTHONPATH=src /workspace/apm-stage1/.venv/bin/python scripts/stage6/gpu_compare.py \
  --subset comparison --model-path /workspace/models/qwen2.5-14b-instruct \
  --authorization-start-utc NEW_AUTHORIZATION_START_IN_ISO_UTC
PYTHONPATH=src /workspace/apm-stage1/.venv/bin/python scripts/stage6/report.py
```

This records a new authorization in a fresh ledger, verifies the frozen inputs,
weights, BF16 GPU placement and backend, and executes each episode once. Original
results must never be overwritten. The preserved Stage 5 full-bound capacity
check applies to this same device/checkpoint/runtime. A changed device requires
its own verification. No model downloads or new inference are needed for review.

The browser inspection uses `scripts/stage6/browser_inspect.py --chromium
/snap/bin/chromium` with Playwright in the local review environment. It opens
self-contained files, starts no server and preserves screenshots in `inspection/`.
`human_packet.py` builds offline review material after that inspection, never an
agent-visible input. Run those in a copied result workspace to preserve originals.

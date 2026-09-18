# Stage 4 reproduction

Use the existing project `.venv`; dependency versions remain in `requirements.lock`.
Run from the repository root. These commands do not start model inference:

```bash
.venv/bin/python -m pytest -q tests/test_stage3.py tests/test_stage4.py
.venv/bin/python scripts/stage4/verify.py --replay --output /tmp/stage4-verification.json
.venv/bin/python - <<'PY'
from trajectory_dashboards.stage4.core import Engine
from trajectory_dashboards.stage4.display import replay
replay(Engine(), 'artifacts/stage4/pilot/baseline/s4_01/accepted', '/tmp/stage4-replay')
PY
```

Open `/tmp/stage4-replay/dashboard.html`. Exports are self-contained and need no
server. Accepted compact outputs also contain `selection_provenance.json` with
the exact semantic answer and every compiler contribution. Replay/recompilation
does not dispatch additional analyses or invoke a model. Choose fresh output
directories; saved output/report commands refuse overwriting.

Reproduce structural selection and independent facts in a separate directory:

```bash
.venv/bin/python scripts/stage4/new_workspace.py /tmp/stage4-prepare --prepare
cd /tmp/stage4-prepare
PYTHONPATH=src /absolute/path/to/repository/.venv/bin/python scripts/stage4/prepare.py
```

People/questions and independent numerical facts reproduce. Fresh creation times
and source-manifest provenance hashes differ. This loads only development features
and the pre-existing split identifiers. No new raw data or model download is needed.

Recompute an analysis in the repository using the same unchanged baseline/backend:

```bash
.venv/bin/python - <<'PY'
from trajectory_dashboards.common import read_json
from trajectory_dashboards.stage4.core import Engine
from trajectory_dashboards.stage2.methods import deterministic
from trajectory_dashboards.stage4.display import render
q = read_json('artifacts/stage4/tasks/manifest.json')['tasks'][0]['question']
e = Engine()
spec, evidence, requests = deterministic(e, q)
render(e, q, spec, evidence, '/tmp/stage4-analysis')
PY
```

To repeat offline scoring, create a fresh frozen workspace with `new_workspace.py`,
copy the saved Stage 4 `pilot/`, `gpu/` and `model_ledger.jsonl` into it, and run
`PYTHONPATH=src /absolute/path/to/repository/.venv/bin/python scripts/stage4/report.py`.
No model runs. The Stage 3 diagnosis is `scripts/stage4/diagnose_stage3.py`; run in
a separate complete checkout with a fresh `artifacts/stage4/diagnostics/` destination.
Original Stage 3 outputs and scores are only read. It includes oracle assistance
and must never be used as an inference-time answer selector.

Optional GPU reproduction requires a fresh independently authorized budget. On
the existing GPU host, reuse downloaded weights and its environment:

```bash
PYTHONPATH=src /workspace/apm-stage1/.venv/bin/python scripts/stage4/new_workspace.py /workspace/stage4-independent
cd /workspace/stage4-independent
PYTHONPATH=src /workspace/apm-stage1/.venv/bin/python scripts/stage4/baseline.py
PYTHONPATH=src /workspace/apm-stage1/.venv/bin/python scripts/stage4/gpu_pilot.py \
  --subset pilot --model-path /workspace/apm-stage1/models/qwen \
  --authorization-start-utc YOUR_NEW_AUTHORIZATION_START_IN_ISO_UTC
PYTHONPATH=src /workspace/apm-stage1/.venv/bin/python scripts/stage4/report.py
```

This is additional research, not part of the completed pilot. The runner verifies
frozen inputs and pinned weight hashes, requires actual CUDA execution, counts
all attempted generations and process time in append-only ledgers, and refuses
to repeat any started episode. Shared initialization/profile overhead is separate.
No fallback turns a failed episode into an agent success.

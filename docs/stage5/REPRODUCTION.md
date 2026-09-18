# Stage 5 reproduction

Use the existing project `.venv` with `requirements.lock`; run from repository root.
Saved outputs require no model weights, raw data, new download or inference.
Choose fresh destinations: result/scoring commands refuse replacement.

```bash
.venv/bin/python -m pytest -q tests/test_stage5.py
.venv/bin/python scripts/stage5/verify.py --replay --output /tmp/stage5-verification.json
.venv/bin/python - <<'PY'
from trajectory_dashboards.stage5.core import Engine
from trajectory_dashboards.stage5.adapter import replay
replay(Engine(), 'artifacts/stage5/comparison/baseline/s5_01/accepted', '/tmp/stage5-replay')
PY
```

Open `/tmp/stage5-replay/dashboard.html`. Every accepted agent output has the same
replay path shape under its condition (`qwen7b_full_spec`, `qwen7b_semantic`,
`qwen14b_full_spec`, `qwen14b_semantic`). The bound result, semantic selection and
compiler provenance remain inspectable. There is no server to start.

Reproduce the new selection and independently calculated facts:

```bash
.venv/bin/python scripts/stage5/new_workspace.py /tmp/stage5-preparation --prepare
cd /tmp/stage5-preparation
PYTHONPATH=src /absolute/path/to/repository/.venv/bin/python scripts/stage5/prepare.py
```

People, questions and numerical facts should match; fresh timestamps/source
manifest provenance will differ. Only development features and split identifiers
are read. To repeat CPU analysis, use the unchanged baseline method:

```bash
.venv/bin/python - <<'PY'
from trajectory_dashboards.common import read_json
from trajectory_dashboards.stage2.methods import deterministic
from trajectory_dashboards.stage5.core import Engine
from trajectory_dashboards.stage5.adapter import render
q = read_json('artifacts/stage5/tasks/manifest.json')['tasks'][0]['question']
engine = Engine()
spec, evidence, requests = deterministic(engine, q)
render(engine, q, spec, evidence, '/tmp/stage5-analysis')
PY
```

For offline rescoring, create a fresh frozen workspace with `new_workspace.py`
(without `--prepare`), copy saved `artifacts/stage5/comparison/`, `gpu/` and
`model_ledger.jsonl` to matching paths, then run `scripts/stage5/report.py` using
`PYTHONPATH=src` and the existing repository Python. The imported scorer is unchanged.

Optional new GPU reproduction requires separate authorization and a fresh budget.
On the existing GPU host, reuse both downloaded checkpoints. From a complete
review checkout, create a fresh destination with `new_workspace.py`, change into
it, then run (the first override is recorded and persists across subsequent loads):

```bash
PYTHONPATH=src /workspace/apm-stage1/.venv/bin/python scripts/stage5/baseline.py
PYTHONPATH=src /workspace/apm-stage1/.venv/bin/python scripts/stage5/gpu_compare.py \
  --subset comparison --model-key qwen7b --model-path /workspace/apm-stage1/models/qwen \
  --authorization-start-utc NEW_AUTHORIZATION_START_IN_ISO_UTC
PYTHONPATH=src /workspace/apm-stage1/.venv/bin/python scripts/stage5/gpu_compare.py \
  --subset comparison --model-key qwen14b --model-path /workspace/models/qwen2.5-14b-instruct
PYTHONPATH=src /workspace/apm-stage1/.venv/bin/python scripts/stage5/report.py
```

The pinned hashes, existing capacity proofs and freeze are checked. A reproduction
on changed hardware requires its own capacity verification; do not silently reuse
the device claim. The original acquisition commands were `scripts/stage5/acquire.py
inspect --model-path /workspace/models/qwen2.5-14b-instruct` followed by `download`
with the same path; inspection resolves the official revision before shard
download. To reproduce this experiment specifically, use the recorded revision
and manifest, not a newly resolved main checkpoint. Do not download again merely
to inspect the review.

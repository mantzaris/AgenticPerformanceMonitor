"""Run on the existing GPU host. Downloads only one pinned public model, no inference."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from huggingface_hub import HfApi, snapshot_download

MODEL = "Qwen/Qwen2.5-7B-Instruct"
REVISION = "a09a35458c702b33eeacc393d103063234e8bc28"
root = Path("models/qwen")
info = HfApi().model_info(MODEL, revision=REVISION, files_metadata=True)
assert info.sha == REVISION
allowed = [s for s in info.siblings if s.rfilename.endswith((".json", ".safetensors", ".txt")) or s.rfilename in {"LICENSE", "README.md"}]
assert sum(s.size or 0 for s in allowed) < 20_000_000_000
snapshot_download(MODEL, revision=REVISION, local_dir=root, allow_patterns=[s.rfilename for s in allowed], max_workers=4)
files = {}
for s in allowed:
    p = root / s.rfilename
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(b)
    if s.lfs:
        assert h.hexdigest() == s.lfs.sha256
    files[s.rfilename] = {"sha256": h.hexdigest(), "bytes": p.stat().st_size, "expected_lfs_sha256": s.lfs.sha256 if s.lfs else None}
out = Path("artifacts/gpu")
out.mkdir(parents=True, exist_ok=True)
(out / "model_manifest.json").write_text(json.dumps({"model": MODEL, "revision": REVISION, "license": "Apache-2.0", "source": "https://huggingface.co/"+MODEL, "retrieved_utc": datetime.now(timezone.utc).isoformat(), "total_bytes": sum(x["bytes"] for x in files.values()), "files": files}, indent=2)+"\n")
print("Model download and checksum verification complete.", flush=True)

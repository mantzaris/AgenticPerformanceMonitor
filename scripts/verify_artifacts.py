"""Replay every saved result and check the actual handoff, without model imports."""
from html import escape
from pathlib import Path
import tempfile
import pandas as pd
from trajectory_dashboards.common import digest, file_hash, now, read_json, write_json
from trajectory_dashboards.dashboard import replay

w = pd.read_parquet("data/prepared/weekly.parquet")
splits = read_json("artifacts/data/splits.json")["assignments"]
assert not set(splits["development"]) & set(splits["reserved"])
assert set(w.person_id) <= set(splits["development"])
assert not w.duplicated(["person_id", "course", "week"]).any()
assert w.end_day.max() == 83
assert not {"score", "final_result", "date_unregistration", "studied_credits"} & set(w.columns)
for x in read_json("artifacts/data/manifest.json")["relationships"].values():
    if isinstance(x,dict):
        assert x["multiplication"] == 0
sources = sorted(Path("artifacts/deterministic").glob("dev_*"))
sources += sorted(Path("artifacts/gpu").glob("dev_*/accepted"))
sources += sorted(Path("artifacts/gpu").glob("dev_*/deterministic_fallback"))
results = []
with tempfile.TemporaryDirectory(prefix="apm-replay-") as tmp:
    for i,source in enumerate(sources):
        output = Path(tmp) / str(i)
        replay(source,output)
        actual,expected = read_json(output/"bound.json"),read_json(source/"bound.json")
        assert actual == expected
        html = (output/"dashboard.html").read_text()
        assert all(escape(c["text"]) in html for c in actual["claims"])
        assert all(f'id="{eid}"' in html for eid in actual["evidence_hashes"])
        assert read_json(output/"chart.vl.json") == read_json(source/"chart.vl.json")
        results.append({"source": str(source), "status": "PASS", "bound_sha256": file_hash(source/"bound.json"), "png_bytes": (output/"dashboard.png").stat().st_size, "svg_exact_replay": file_hash(output/"dashboard.svg")==file_hash(source/"dashboard.svg")})
runtime = read_json("artifacts/gpu/runtime.json")
assert runtime["parameter_devices"] == ["cuda:0"]
assert runtime["parameter_dtypes"] == ["torch.bfloat16"]
assert runtime["cuda_kernel_proof"]["kernel_events"] > 0
assert runtime["cumulative_generations"] <= 20
assert runtime["cumulative_gpu_process_seconds"] <= 7200
assert len(list(Path("artifacts/gpu/generations").glob("*.output.txt"))) == runtime["cumulative_generations"]
assert len(runtime["results"]) == 3
assert all(x["final_repairs"] <= 1 for x in runtime["results"])
write_json("artifacts/verification.json", {"verified_utc": now(), "checks": ["Unique person/course/week grid", "No reserved people in prepared data", "No post-cutoff feature or forbidden raw field", "Audited dimension joins preserve row counts", "Saved quantitative claims and chart specifications replay exactly", "All HTML evidence links resolve", "Intended GPU device, dtype, CUDA device events and budget ledger verified"], "replays": results, "agent_results": runtime["results"]})
print(f"Verified {len(results)} complete saved dashboards without inference.")

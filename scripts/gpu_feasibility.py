"""Single-model bounded tool loop. Run in the repository root on the existing pod."""
from __future__ import annotations

import time
PROCESS_START = time.monotonic()
import argparse
import contextlib
import gc
import importlib.metadata as metadata
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
from datetime import datetime, timezone

from trajectory_dashboards.common import code_hash, commit, digest, now, read_json, write_json
from trajectory_dashboards.contracts import AnalysisRequest, DashboardSpecification, RunManifest
from trajectory_dashboards.analysis import Engine
from trajectory_dashboards.dashboard import deterministic_spec, render, requests_for


def append(path, event):
    with open(path, "a") as f:
        f.write(json.dumps({"utc": now(), **event}, allow_nan=False) + "\n")
        f.flush()
        os.fsync(f.fileno())


def gpu_process():
    text = subprocess.check_output(["nvidia-smi", "--query-compute-apps=pid,process_name,used_memory", "--format=csv,noheader,nounits"], text=True)
    return [line for line in text.splitlines() if line.split(",")[0].strip() == str(os.getpid())]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model-path", default="models/qwen")
    p.add_argument("--output", default="artifacts/gpu")
    p.add_argument("--authorized-start-utc", help="Explicit new execution authorization for a later independent rerun; omitted in original Stage 1")
    args = p.parse_args()
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    cfg = read_json("configs/stage1.json")
    ledger = out / "ledger.jsonl"
    import fcntl
    lock = open(out / "budget.lock", "a")
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    events = [json.loads(x) for x in ledger.read_text().splitlines()] if ledger.exists() else []
    started = [x for x in events if x["event"] == "process_started"]
    ended = [x for x in events if x["event"] == "process_finished"]
    if len(started) != len(ended):
        raise RuntimeError("Unclosed model-process reservation; reconcile elapsed time before retry")
    used_seconds = sum(x["elapsed_seconds"] for x in ended)
    generations = sum(x["event"] == "generation_started" for x in events)
    deadline = datetime.fromisoformat(cfg["deadline_utc"].replace("Z", "+00:00"))
    if args.authorized_start_utc:
        from datetime import timedelta
        if events:
            raise ValueError("A new authorization requires a new output directory; original ledger is immutable")
        deadline = datetime.fromisoformat(args.authorized_start_utc.replace("Z", "+00:00")) + timedelta(seconds=cfg["wall_seconds_limit"])
    remaining = min(cfg["gpu_process_seconds_limit"] - used_seconds, (deadline - datetime.now(timezone.utc)).total_seconds())
    if remaining <= 0 or generations >= cfg["generation_limit"]:
        raise RuntimeError("Stage/model budget exhausted")
    def stop(signum, frame):
        raise TimeoutError("GPU process or stage deadline reached")
    signal.signal(signal.SIGALRM, stop)
    signal.signal(signal.SIGTERM, stop)
    signal.alarm(max(1, int(remaining)))
    append(ledger, {"event": "process_started", "pid": os.getpid(), "remaining_seconds": remaining})
    runtime = {"started_utc": now(), "model": cfg["model"], "revision": cfg["model_revision"], "backend": "transformers", "precision": "bfloat16", "quantization": "none", "cpu_offload": False, "warmup_generations": 0, "generation_count_before": generations, "results": [], "sampling": {"do_sample": False, "max_new_tokens": cfg["max_new_tokens"]}, "code_sha256": code_hash(), "code_commit": commit(), "status": "running"}
    model = None
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        runtime["environment"] = {name: metadata.version(name) for name in ["torch", "transformers", "accelerate", "huggingface-hub", "numpy", "pandas", "pydantic"]}
        runtime["environment"].update(python=sys.version, cuda_runtime=torch.version.cuda)
        if not torch.cuda.is_available():
            raise RuntimeError("No CUDA device; CPU fallback forbidden")
        runtime["gpu"] = subprocess.check_output(["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"], text=True).strip()
        manifest = read_json("artifacts/gpu/model_manifest.json")
        if manifest["revision"] != cfg["model_revision"]:
            raise ValueError("Wrong model revision")
        tokenizer = AutoTokenizer.from_pretrained(args.model_path, local_files_only=True)
        model = AutoModelForCausalLM.from_pretrained(args.model_path, local_files_only=True, torch_dtype=torch.bfloat16, device_map={"": "cuda:0"}, attn_implementation="sdpa").eval()
        runtime["parameter_devices"] = sorted(set(str(p.device) for p in model.parameters()))
        runtime["parameter_dtypes"] = sorted(set(str(p.dtype) for p in model.parameters()))
        if runtime["parameter_devices"] != ["cuda:0"]:
            raise RuntimeError("Model is not entirely on intended GPU")
        runtime["memory_after_load_bytes"] = torch.cuda.memory_allocated()
        runtime["nvidia_smi_own_process_after_load"] = gpu_process()
        engine = Engine()
        runtime["prepared_data_sha256"] = engine.meta["files"]
        write_json(out / "runtime_running.json", runtime)

        def generate(messages, question_id, phase):
            nonlocal generations
            if time.monotonic() - PROCESS_START >= remaining or datetime.now(timezone.utc) >= deadline:
                raise TimeoutError("GPU process or stage deadline reached")
            if generations >= cfg["generation_limit"]:
                raise RuntimeError("Generation limit reached")
            generations += 1
            stem = out / "generations" / f"{generations:02d}_{question_id}_{phase}"
            stem.parent.mkdir(exist_ok=True)
            write_json(str(stem)+".input.json", messages)
            append(ledger, {"event": "generation_started", "generation": generations, "question_id": question_id, "phase": phase})
            record = {"generation": generations, "question_id": question_id, "phase": phase, "started_utc": now()}
            started_at = time.monotonic()
            try:
                text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                inputs = tokenizer(text, return_tensors="pt").to("cuda:0")
                record["prompt_tokens"] = inputs.input_ids.shape[1]
                record["input_device"] = str(inputs.input_ids.device)
                if inputs.input_ids.shape[1] > 12000:
                    raise ValueError("Prompt exceeds bounded context")
                event_start, event_end = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
                profile = torch.profiler.profile(activities=[torch.profiler.ProfilerActivity.CPU, torch.profiler.ProfilerActivity.CUDA]) if generations == 1 else contextlib.nullcontext()
                with profile as prof, torch.inference_mode():
                    event_start.record()
                    generated = model.generate(**inputs, do_sample=False, max_new_tokens=cfg["max_new_tokens"], pad_token_id=tokenizer.eos_token_id)
                    event_end.record()
                    torch.cuda.synchronize()
                if prof:
                    kernels = [e for e in prof.events() if e.device_type == torch.autograd.DeviceType.CUDA]
                    runtime["cuda_kernel_proof"] = {"generation": generations, "kernel_events": len(kernels), "sample_kernel_names": list(dict.fromkeys(e.name for e in kernels))[:12], "total_device_time_us": float(sum(e.device_time_total for e in kernels))}
                    if not kernels:
                        raise RuntimeError("Profiler did not record CUDA execution")
                raw = tokenizer.decode(generated[0, inputs.input_ids.shape[1]:], skip_special_tokens=True)
                Path(str(stem)+".output.txt").write_text(raw)
                record.update(status="completed", completion_tokens=int(generated.shape[1]-inputs.input_ids.shape[1]), output_device=str(generated.device), cuda_event_ms=float(event_start.elapsed_time(event_end)), allocated_bytes=int(torch.cuda.memory_allocated()), peak_allocated_bytes=int(torch.cuda.max_memory_allocated()), nvidia_smi_own_process=gpu_process())
                return raw
            except Exception as exc:
                record.update(status="failed", error=f"{type(exc).__name__}: {exc}")
                raise
            finally:
                record["elapsed_seconds"] = time.monotonic()-started_at
                write_json(str(stem)+".metadata.json", record)
                append(ledger, {"event": "generation_finished", **record})

        for q in engine.questions.values():
            case = out / q.question_id
            case.mkdir(exist_ok=True)
            result = {"question_id": q.question_id, "status": "failed", "tool_calls_executed": 0, "final_repairs": 0}
            evidence = {}
            # This is an explicitly constrained feasibility policy, not a generic-agent baseline.
            required_refs = ["course", "same_prior_attempt", "early_stage"] if q.kind == "reference_sensitivity" else ["course"]
            required_features = ["clicks_per_eligible_day", "scheduled_no_submission"] if q.kind == "measurement_limits" else ["clicks_per_eligible_day"]
            system = "You investigate recorded OULAD activity using a typed analytical tool. Output ONLY a JSON object, no Markdown or explanation. Never compute or invent measurements. This is a constrained feasibility test. First request analyses; after actual tool results, return a dashboard specification. Clicks are not effort or ability. Scores are withheld."
            prompt = {"question": q.model_dump(), "task": "Request the analyses needed for this question. Return {\"tool_calls\": [AnalysisRequest, ...]}. Maximum six calls. Use start_week=8,end_week=11. Include each required reference and feature with course as the feature comparison reference.", "required_references": required_refs, "required_features": required_features, "tool_schema": AnalysisRequest.model_json_schema()}
            messages = [{"role": "system", "content": system}, {"role": "user", "content": json.dumps(prompt)}]
            try:
                raw = generate(messages, q.question_id, "tools")
                calls = json.loads(raw)
                if set(calls) != {"tool_calls"} or not 1 <= len(calls["tool_calls"]) <= 6:
                    raise ValueError("Expected 1–6 typed tool calls")
                requests = [AnalysisRequest.model_validate(r) for r in calls["tool_calls"]]
                if any(r.question_id != q.question_id for r in requests):
                    raise ValueError("Cross-question tool request")
                for r in requests:
                    e = engine.analyze(r)
                    evidence[e.evidence_id] = e
                    result["tool_calls_executed"] += 1
                write_json(case / "tool_calls.json", [r.model_dump() for r in requests])
                write_json(case / "tool_results.json", {k:e.model_dump() for k,e in evidence.items()})
                compact = [{"evidence_id": e.evidence_id, "feature": e.feature, "unit": e.unit, "reference": e.reference, "reference_label": e.reference_label, "status": e.status, "window": e.window, "people": e.people, "observations": e.observations, "summary": e.summary, "observation_states": sorted(set(r["observation_status"] for r in e.observation_status)), "limitations": e.limitations} for e in evidence.values()]
                messages += [{"role": "assistant", "content": raw}, {"role": "tool", "name": "analyze", "content": json.dumps(compact)}, {"role": "user", "content": json.dumps({"task": "Return the final DashboardSpecification ONLY. Use actual evidence IDs from the tool results. Include all required evidence. Every evidence ID must have a claim AND a trajectory or comparison panel. Include an observation_status panel and a trajectory panel. For personal_change include a personal_change claim. For measurement_limits include an assessment_status panel and measurement_limits claim. No numerical values or extra text fields belong in the specification. Use at most six panels.", "annotation": {"personal_change": "descriptive_only", "reference_sensitivity": "reference_dependent", "measurement_limits": "measurement_limited"}[q.kind], "schema": DashboardSpecification.model_json_schema()})}]
                for attempt in range(2):
                    raw_final = generate(messages, q.question_id, "final" if attempt == 0 else "repair")
                    try:
                        spec = DashboardSpecification.model_validate_json(raw_final)
                        render(spec, evidence, q, case / "accepted")
                        result["status"] = "agent_generated_and_accepted" if attempt == 0 else "agent_generated_and_repaired"
                        break
                    except Exception as exc:
                        error = f"{type(exc).__name__}: {exc}"
                        write_json(case / f"validation_error_{attempt}.json", {"error": error, "original_output": raw_final})
                        if attempt == 1:
                            raise
                        result["final_repairs"] = 1
                        messages += [{"role": "assistant", "content": raw_final}, {"role": "user", "content": "Validation failed. You have one repair. Return the complete valid JSON only. Error: " + error}]
            except TimeoutError:
                raise
            except Exception as exc:
                result["error"] = f"{type(exc).__name__}: {exc}"
                fallback = [engine.analyze(r) for r in requests_for(q)]
                render(deterministic_spec(q, fallback), {e.evidence_id:e for e in fallback}, q, case / "deterministic_fallback")
                result["fallback_status"] = "deterministic_fallback; NOT agent success"
            runtime["results"].append(result)
            write_json(out / "runtime_running.json", runtime)
            print(json.dumps(result), flush=True)
        runtime["status"] = "completed"
    except Exception as exc:
        runtime.update(status="failed", error=f"{type(exc).__name__}: {exc}")
        raise
    finally:
        if model is not None:
            del model
            gc.collect()
            import torch
            torch.cuda.empty_cache()
        elapsed = time.monotonic() - PROCESS_START
        runtime.update(completed_utc=now(), gpu_process_elapsed_seconds=elapsed, cumulative_gpu_process_seconds=used_seconds+elapsed, generations_this_process=generations-runtime["generation_count_before"], cumulative_generations=generations, billing_time="unknown; not inferred from GPU process time")
        write_json(out / "runtime.json", runtime)
        append(ledger, {"event": "process_finished", "elapsed_seconds": elapsed, "generation_count": generations})
        signal.alarm(0)


if __name__ == "__main__":
    main()

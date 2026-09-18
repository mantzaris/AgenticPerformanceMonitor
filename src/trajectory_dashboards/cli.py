import argparse
from pathlib import Path
from .common import write_json


def main():
    p = argparse.ArgumentParser(description="Stage 1 OULAD pipeline")
    sub = p.add_subparsers(dest="command", required=True)
    for name in ["download", "prepare", "analyze", "schemas"]:
        sub.add_parser(name)
    r = sub.add_parser("replay")
    r.add_argument("source")
    r.add_argument("--output", required=True)
    args = p.parse_args()
    if args.command == "download":
        from .acquire import acquire
        acquire()
    elif args.command == "prepare":
        from .acquire import audit
        from .prepare import prepare
        audit()
        prepare()
    elif args.command == "analyze":
        from .analysis import Engine, fit_models
        from .dashboard import deterministic_spec, render, requests_for
        engine = Engine()
        fit_models(engine)
        for q in engine.questions.values():
            records = [engine.analyze(r) for r in requests_for(q)]
            render(deterministic_spec(q, records), {e.evidence_id:e for e in records}, q, Path("artifacts/deterministic") / q.question_id)
            print(f"Rendered {q.question_id}", flush=True)
    elif args.command == "replay":
        from .dashboard import replay
        replay(args.source, args.output)
    else:
        from .contracts import DatasetManifest, Question, AnalysisRequest, EvidenceRecord, ClaimRecord, DashboardSpecification, RunManifest
        for cls in [DatasetManifest, Question, AnalysisRequest, EvidenceRecord, ClaimRecord, DashboardSpecification, RunManifest]:
            write_json(Path("artifacts/schemas") / (cls.__name__+".json"), cls.model_json_schema())


if __name__ == "__main__":
    main()

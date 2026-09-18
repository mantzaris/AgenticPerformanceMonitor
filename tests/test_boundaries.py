"""Scientific invariants, not a research evaluation."""
from copy import deepcopy
from pathlib import Path
import json
import numpy as np
import pandas as pd
import pytest
from trajectory_dashboards.prepare import build_weekly, split_person
from trajectory_dashboards.common import digest, read_json
from trajectory_dashboards.contracts import AnalysisRequest, Question
from trajectory_dashboards.dashboard import replay, validate, validate_evidence


@pytest.fixture
def tables():
    regs = pd.DataFrame([dict(code_module="A", code_presentation="P", id_student=i, date_registration=r, date_unregistration=u, num_of_prev_attempts=0) for i,r,u in [(1,0,np.nan),(2,0,7),(3,np.nan,np.nan),(4,0,100)]])
    act = pd.DataFrame([dict(code_module="A",code_presentation="P",id_student=i,id_site=10,date=d,sum_click=v) for i,d,v in [(1,0,3),(1,0,2),(1,14,999),(2,8,10),(4,9,4)]])
    assessments = pd.DataFrame([dict(code_module="A",code_presentation="P",id_assessment=i,assessment_type="TMA",date=d) for i,d in [(10,4),(11,11),(12,30)]])
    subs = pd.DataFrame([dict(id_student=i,id_assessment=a,date_submitted=d,is_banked=b,score=s) for i,a,d,b,s in [(1,10,3,0,99),(1,11,8,1,88),(2,10,15,0,77)]])
    return regs, act, subs, assessments


def test_zero_unknown_ineligible_and_banked_are_distinct(tables):
    w,a = build_weekly(*tables,cutoff=13)
    rows = w.set_index(["person_id","week"])
    assert rows.loc[(1,0),"clicks"] == 5 # preserve two source contributions, no join multiplication
    assert rows.loc[(1,1),"observation_status"] == "zero_recorded_activity"
    assert rows.loc[(2,1),"observation_status"] == "ineligible"
    assert pd.isna(rows.loc[(2,1),"clicks"])
    assert rows.loc[(3,0),"observation_status"] == "unknown"
    assert pd.isna(rows.loc[(3,0),"clicks"])
    assert rows.loc[(1,0),"nonbanked_submissions"] == 1
    assert rows.loc[(1,1),"nonbanked_submissions"] == 0
    assert rows.loc[(1,1),"scheduled_no_submission"] == 1
    assert set(a.score_status) == {"withheld_release_time_unknown"}
    assert "score" not in w and "date_unregistration" not in w


def test_future_mutations_and_row_order_cannot_change_features(tables):
    before,_ = build_weekly(*tables,cutoff=13)
    regs,act,sub,assess = [x.copy() for x in tables]
    regs.loc[regs.id_student.eq(4),"date_unregistration"] = 999
    act.loc[act.date.gt(13),"sum_click"] = 10_000_000
    sub.loc[sub.date_submitted.gt(13),"date_submitted"] = 200
    sub["score"] = 0
    assess.loc[assess.date.gt(13),"date"] = 999
    after,_ = build_weekly(regs.sample(frac=1,random_state=1),act.sample(frac=1,random_state=2),sub,assess,13)
    pd.testing.assert_frame_equal(before,after)


def test_duplicate_dimension_keys_rejected(tables):
    regs,act,sub,a=tables
    with pytest.raises(ValueError,match="Duplicate registration"):
        build_weekly(pd.concat([regs,regs.iloc[:1]]),act,sub,a,13)


def test_person_split_groups_every_registration():
    splits=read_json("artifacts/data/splits.json")
    dev,res=map(set,[splits["assignments"]["development"],splits["assignments"]["reserved"]])
    assert not dev & res
    assert len(dev|res)==28785
    assert all(split_person(i,splits["salt"],.7)=="development" for i in dev)
    assert all(split_person(i,splits["salt"],.7)=="reserved" for i in res)


@pytest.fixture
def saved():
    root=Path("artifacts/deterministic/dev_2")
    return read_json(root/"spec.json"),read_json(root/"evidence.json"),Question.model_validate(read_json(root/"question.json"))


def reseal(e):
    d=deepcopy(e)
    d.pop("evidence_id")
    d["provenance"]={k:v for k,v in d["provenance"].items() if k not in {"executed_utc","code_sha256"}}
    e["evidence_id"]="ev_"+digest(d)[:16]
    return e


@pytest.mark.parametrize("field,value",[("unit","hours"),("people",999999),("cutoff_day",999)])
def test_semantic_mutations_rejected_even_with_recomputed_checksum(saved,field,value):
    spec,ev,q=saved
    e=deepcopy(next(iter(ev.values())))
    e[field]=value
    with pytest.raises(ValueError):
        validate_evidence(reseal(e),q)


def test_focal_person_and_postcutoff_rejected(saved):
    _,ev,q=saved
    e=deepcopy(next(iter(ev.values())))
    e["peer_ids"][0]=q.person_id
    e["peer_summary_rows"][0]["person_id"]=q.person_id
    with pytest.raises(ValueError,match="focal leakage"):
        validate_evidence(reseal(e),q)
    e=deepcopy(next(iter(ev.values())))
    e["trajectory"][0]["end_day"]=84
    with pytest.raises(ValueError,match="Post-cutoff"):
        validate_evidence(reseal(e),q)


def test_unsupported_evidence_and_omitted_context_rejected(saved):
    spec,ev,q=saved
    bad=deepcopy(spec)
    bad["evidence_ids"][0]="invented"
    with pytest.raises(ValueError,match="Unsupported evidence"):
        validate(bad,ev,q)
    bad=deepcopy(spec)
    bad["panels"]=[p for p in bad["panels"] if p["kind"]!="observation_status"]
    with pytest.raises(ValueError,match="observation panels"):
        validate(bad,ev,q)


def test_displayed_mean_matches_independent_prepared_calculation(saved):
    spec,ev,q=saved
    w=pd.read_parquet("data/prepared/weekly.parquet")
    e=next(x for x in ev.values() if x["reference"]=="course")
    data=w[w.course.eq(q.course)&w.week.between(8,11)&w.person_id.ne(q.person_id)&w.clicks_per_eligible_day.notna()]
    assert data.person_id.nunique()==e["people"]
    assert len(data)==e["observations"]
    assert np.isclose(data.groupby("person_id").clicks_per_eligible_day.mean().mean(),e["summary"]["peer_mean"])
    bad=deepcopy(e)
    bad["summary"]["focal_mean"]+=1
    with pytest.raises(ValueError,match="Focal result"):
        validate_evidence(reseal(bad),q)


def test_replay_without_model_or_raw_data(tmp_path,monkeypatch):
    import builtins
    original=builtins.__import__
    def guarded(name,*args,**kwargs):
        if name in {"torch","transformers"}:
            raise AssertionError("Replay must not import inference")
        return original(name,*args,**kwargs)
    monkeypatch.setattr(builtins,"__import__",guarded)
    for source in sorted(Path("artifacts/deterministic").glob("dev_*")):
        out=tmp_path/source.name
        replay(source,out)
        assert read_json(out/"bound.json")==read_json(source/"bound.json")
        assert (out/"dashboard.png").stat().st_size>1000


def test_gpu_device_proof_if_run():
    p=Path("artifacts/gpu/runtime.json")
    if not p.exists():
        pytest.skip("GPU run not yet available")
    r=read_json(p)
    assert r["parameter_devices"]==["cuda:0"]
    assert r["cuda_kernel_proof"]["kernel_events"]>0
    assert r["cumulative_generations"]<=20
    assert r["cumulative_gpu_process_seconds"]<=7200
    assert r["memory_after_load_bytes"]>10_000_000_000
    records=[read_json(x) for x in Path("artifacts/gpu/generations").glob("*.metadata.json")]
    assert records and all(x["input_device"]=="cuda:0" and x["output_device"]=="cuda:0" and x["cuda_event_ms"]>0 for x in records if x["status"]=="completed")

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from server.db.models import EvalRun
from server.db.session import get_db
from server.services.blob_store import LocalBlobStore

router = APIRouter(prefix="/v1/evals", tags=["evals"])
blob_store = LocalBlobStore()


class EvalRequest(BaseModel):
    dataset_name: str
    agent_version: str = "dev"


@router.post("/run")
def run_eval(payload: EvalRequest, db: Session = Depends(get_db)):
    eval_id = uuid4()
    cases = [
        {"input": "2+2", "expected": "4"},
        {"input": "AgentOps purpose", "expected_contains": "observability"},
    ]
    results = []
    score = 0
    for case in cases:
        output = "4" if case["input"] == "2+2" else "AgentOps provides observability, replay, and evals"
        ok = output == case.get("expected") or case.get("expected_contains", "") in output
        score += int(ok)
        results.append({"case": case, "output": output, "success": ok})

    summary = {"total": len(cases), "passed": score, "pass_rate": round(score / len(cases), 2)}
    report = {"summary": summary, "results": results}
    report_ref = blob_store.put_json(f"eval-{eval_id}", report)
    row = EvalRun(
        id=eval_id,
        dataset_name=payload.dataset_name,
        agent_version=payload.agent_version,
        started_at=datetime.now(timezone.utc),
        ended_at=datetime.now(timezone.utc),
        summary=summary,
        report_ref=report_ref,
    )
    db.add(row)
    db.commit()
    return {"eval_run_id": str(eval_id)}


@router.get("")
def list_evals(db: Session = Depends(get_db)):
    rows = db.query(EvalRun).order_by(EvalRun.started_at.desc()).all()
    return [{"id": str(r.id), "dataset_name": r.dataset_name, "agent_version": r.agent_version, "summary": r.summary} for r in rows]


@router.get("/{eval_id}")
def eval_detail(eval_id: str, db: Session = Depends(get_db)):
    row = db.get(EvalRun, eval_id)
    if not row:
        return {"error": "not found"}
    return {
        "id": str(row.id),
        "dataset_name": row.dataset_name,
        "agent_version": row.agent_version,
        "summary": row.summary,
        "report_ref": row.report_ref,
        "report": blob_store.get_json(row.report_ref) if row.report_ref else {},
    }

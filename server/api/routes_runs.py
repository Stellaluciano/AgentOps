from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from server.db.models import Run, Span
from server.db.session import get_db
from server.services.aggregator import enqueue_aggregation

router = APIRouter(prefix="/v1/runs", tags=["runs"])


class CreateRun(BaseModel):
    id: UUID | None = None
    project: str
    name: str
    status: str = "running"
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    tags: dict = Field(default_factory=dict)
    metadata: dict = Field(default_factory=dict)


class UpdateRun(BaseModel):
    status: str | None = None
    ended_at: datetime | None = None
    tags: dict | None = None
    metadata: dict | None = None


@router.post("")
def create_run(payload: CreateRun, db: Session = Depends(get_db)):
    run = Run(
        id=payload.id,
        project=payload.project,
        name=payload.name,
        status=payload.status,
        started_at=payload.started_at,
        tags=payload.tags,
        metadata=payload.metadata,
    )
    db.add(run)
    db.commit()
    return {"run_id": str(run.id)}


@router.patch("/{run_id}")
def update_run(run_id: str, payload: UpdateRun, db: Session = Depends(get_db)):
    run = db.get(Run, run_id)
    if not run:
        return {"error": "not found"}
    if payload.status:
        run.status = payload.status
    if payload.ended_at:
        run.ended_at = payload.ended_at
    if payload.tags is not None:
        run.tags = payload.tags
    if payload.metadata is not None:
        run.metadata = payload.metadata
    db.commit()

    if run.status in {"completed", "failed"}:
        enqueue_aggregation(str(run.id))

    return {"ok": True}


@router.get("")
def list_runs(project: str | None = Query(default=None), db: Session = Depends(get_db)):
    q = db.query(Run)
    if project:
        q = q.filter(Run.project == project)
    rows = q.order_by(Run.started_at.desc()).limit(100).all()
    return [{"id": str(r.id), "project": r.project, "name": r.name, "status": r.status, "started_at": r.started_at} for r in rows]


@router.get("/{run_id}")
def run_detail(run_id: str, db: Session = Depends(get_db)):
    run = db.get(Run, run_id)
    if not run:
        return {"error": "not found"}
    spans = db.query(Span).filter(Span.run_id == UUID(run_id)).order_by(Span.start_time.asc()).all()
    return {
        "run": {"id": str(run.id), "project": run.project, "name": run.name, "status": run.status, "tags": run.tags, "metadata": run.metadata},
        "spans": [
            {
                "id": str(s.id),
                "parent_id": str(s.parent_id) if s.parent_id else None,
                "type": s.type,
                "name": s.name,
                "status": s.status,
                "start_time": s.start_time,
                "end_time": s.end_time,
                "attrs": s.attrs,
                "payload_ref": s.payload_ref,
            }
            for s in spans
        ],
    }

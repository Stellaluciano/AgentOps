from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from server.db.models import Run, Span
from server.db.session import get_db
from server.services.blob_store import LocalBlobStore

router = APIRouter(prefix="/v1/events", tags=["events"])
blob_store = LocalBlobStore()
LARGE_ATTR_KEYS = {"prompt", "tool_io", "retrieved_docs"}


@router.post("")
async def ingest_events(request: Request, db: Session = Depends(get_db)):
    payload = await request.json()
    events = payload.get("events", [])
    accepted = 0

    for event in events:
        kind = event.get("kind")
        if kind == "run_started":
            run_data = event["run"]
            run = Run(
                id=UUID(run_data["id"]),
                project=run_data["project"],
                name=run_data["name"],
                status=run_data.get("status", "running"),
                started_at=datetime.fromisoformat(run_data["started_at"]),
                tags=run_data.get("tags", {}),
                metadata=run_data.get("metadata", {}),
            )
            db.merge(run)
            accepted += 1
        elif kind == "run_updated":
            run = db.get(Run, event["run_id"])
            if run:
                run.status = event.get("status", run.status)
                run.ended_at = datetime.fromisoformat(event["ended_at"])
                run.metadata = {**(run.metadata or {}), **event.get("metadata", {})}
                accepted += 1
        elif kind == "span":
            span = event["span"]
            attrs = span.get("attrs", {})
            payload_ref = None
            for k in list(attrs.keys()):
                if k in LARGE_ATTR_KEYS:
                    payload_ref = blob_store.put_json(span["id"], {k: attrs.pop(k)})
            db.add(
                Span(
                    id=UUID(span["id"]),
                    run_id=UUID(span["run_id"]),
                    parent_id=UUID(span["parent_id"]) if span.get("parent_id") else None,
                    type=span["type"],
                    name=span["name"],
                    start_time=datetime.fromisoformat(span["start_time"]),
                    end_time=datetime.fromisoformat(span["end_time"]) if span.get("end_time") else datetime.now(timezone.utc),
                    status=span.get("status", "completed"),
                    error_type=span.get("error_type"),
                    attrs=attrs,
                    payload_ref=payload_ref,
                )
            )
            accepted += 1

    db.commit()
    return {"accepted": accepted}

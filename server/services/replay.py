from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from server.db.models import Run, Span


def exact_replay(db: Session, run_id: str) -> str:
    original = db.get(Run, run_id)
    if not original:
        raise ValueError("run not found")
    replay = Run(
        project=original.project,
        name=f"replay:{original.name}",
        status="completed",
        started_at=datetime.now(timezone.utc),
        ended_at=datetime.now(timezone.utc),
        tags={**original.tags, "replay_mode": "exact"},
        metadata={"source_run_id": str(original.id)},
    )
    db.add(replay)
    db.flush()

    for span in db.query(Span).filter(Span.run_id == original.id).all():
        db.add(
            Span(
                run_id=replay.id,
                parent_id=span.parent_id,
                type=span.type,
                name=f"replayed:{span.name}",
                start_time=span.start_time,
                end_time=span.end_time,
                status=span.status,
                error_type=span.error_type,
                attrs={**span.attrs, "replayed": True},
                payload_ref=span.payload_ref,
            )
        )
    db.commit()
    return str(replay.id)

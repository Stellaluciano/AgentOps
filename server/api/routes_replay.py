from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from server.db.session import get_db
from server.services.replay import exact_replay

router = APIRouter(prefix="/v1/replay", tags=["replay"])


class ReplayRequest(BaseModel):
    mode: str = "exact"


@router.post("/{run_id}")
def replay_run(run_id: str, payload: ReplayRequest, db: Session = Depends(get_db)):
    if payload.mode != "exact":
        return {"message": "live replay stubbed", "mode": payload.mode}
    try:
        replay_run_id = exact_replay(db, run_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"replay_run_id": replay_run_id}

from __future__ import annotations

import gzip
import json

from fastapi import Depends, FastAPI, Request

from server.api.routes_events import router as events_router
from server.api.routes_evals import router as evals_router
from server.api.routes_replay import router as replay_router
from server.api.routes_runs import router as runs_router
from server.auth.api_key import require_api_key
from server.db.session import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AgentOps API", version="0.1.0")


@app.middleware("http")
async def gzip_json_middleware(request: Request, call_next):
    if request.headers.get("content-encoding") == "gzip":
        body = await request.body()
        request._body = gzip.decompress(body)

        async def _json():
            return json.loads(request._body)

        request.json = _json
    return await call_next(request)


app.include_router(runs_router, dependencies=[Depends(require_api_key)])
app.include_router(events_router, dependencies=[Depends(require_api_key)])
app.include_router(replay_router, dependencies=[Depends(require_api_key)])
app.include_router(evals_router, dependencies=[Depends(require_api_key)])


@app.get("/health")
def health():
    return {"ok": True}

from __future__ import annotations

import os

from fastapi import Header, HTTPException

API_KEY = os.getenv("AGENTOPS_API_KEY", "dev-api-key")


def require_api_key(x_api_key: str = Header(default="")) -> None:
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="invalid api key")

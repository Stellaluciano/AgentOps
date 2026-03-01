from __future__ import annotations

import gzip
import json
from typing import Any

import requests


class HTTPBatchExporter:
    def __init__(self, base_url: str, api_key: str = "dev-api-key", timeout: float = 10.0):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    def export_events(self, events: list[dict[str, Any]]) -> dict[str, Any]:
        raw = json.dumps({"events": events}).encode("utf-8")
        payload = gzip.compress(raw)
        response = requests.post(
            f"{self.base_url}/v1/events",
            data=payload,
            timeout=self.timeout,
            headers={
                "x-api-key": self.api_key,
                "content-encoding": "gzip",
                "content-type": "application/json",
            },
        )
        response.raise_for_status()
        return response.json()

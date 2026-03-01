from __future__ import annotations

import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .redaction import redact_value


@dataclass
class SpanRecord:
    id: str
    run_id: str
    parent_id: str | None
    type: str
    name: str
    start_time: datetime
    end_time: datetime | None = None
    status: str = "in_progress"
    error_type: str | None = None
    attrs: dict[str, Any] = field(default_factory=dict)


class TraceClient:
    def __init__(self, exporter=None, allowlist: set[str] | None = None):
        self.exporter = exporter
        self.allowlist = allowlist or set()
        self.current_run_id: str | None = None
        self._span_stack: list[SpanRecord] = []
        self._events: list[dict[str, Any]] = []

    def start_run(self, project: str, name: str, tags: dict[str, Any] | None = None, metadata: dict[str, Any] | None = None) -> str:
        self.current_run_id = str(uuid.uuid4())
        self._events.append(
            {
                "kind": "run_started",
                "run": {
                    "id": self.current_run_id,
                    "project": project,
                    "name": name,
                    "status": "running",
                    "started_at": datetime.now(timezone.utc).isoformat(),
                    "tags": tags or {},
                    "metadata": metadata or {},
                },
            }
        )
        return self.current_run_id

    def end_run(self, status: str = "completed", metadata: dict[str, Any] | None = None) -> None:
        if not self.current_run_id:
            return
        self._events.append(
            {
                "kind": "run_updated",
                "run_id": self.current_run_id,
                "status": status,
                "ended_at": datetime.now(timezone.utc).isoformat(),
                "metadata": metadata or {},
            }
        )
        self.flush()
        self.current_run_id = None

    @contextmanager
    def span(self, span_type: str, name: str, attrs: dict[str, Any] | None = None):
        if not self.current_run_id:
            raise RuntimeError("No active run. Call start_run first.")
        span = SpanRecord(
            id=str(uuid.uuid4()),
            run_id=self.current_run_id,
            parent_id=self._span_stack[-1].id if self._span_stack else None,
            type=span_type,
            name=name,
            start_time=datetime.now(timezone.utc),
            attrs=redact_value(attrs or {}, self.allowlist),
        )
        self._span_stack.append(span)
        t0 = time.perf_counter()
        try:
            yield span
            span.status = "completed"
        except Exception as exc:  # noqa: BLE001
            span.status = "failed"
            span.error_type = exc.__class__.__name__
            raise
        finally:
            span.end_time = datetime.now(timezone.utc)
            span.attrs["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
            self._events.append({"kind": "span", "span": _to_wire(span)})
            self._span_stack.pop()

    def flush(self) -> None:
        if not self.exporter or not self._events:
            self._events.clear()
            return
        self.exporter.export_events(list(self._events))
        self._events.clear()


def _to_wire(span: SpanRecord) -> dict[str, Any]:
    return {
        "id": span.id,
        "run_id": span.run_id,
        "parent_id": span.parent_id,
        "type": span.type,
        "name": span.name,
        "start_time": span.start_time.isoformat(),
        "end_time": span.end_time.isoformat() if span.end_time else None,
        "status": span.status,
        "error_type": span.error_type,
        "attrs": span.attrs,
    }

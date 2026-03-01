from __future__ import annotations

from datetime import datetime, timezone
from statistics import quantiles

from sqlalchemy import delete

from server.db.models import RunMetrics, Span
from server.db.session import SessionLocal


COST_PER_1K_TOKENS = 0.002


def aggregate_run_metrics(run_id: str) -> None:
    db = SessionLocal()
    try:
        spans = db.query(Span).filter(Span.run_id == run_id).all()
        if not spans:
            return
        latencies = [float((s.attrs or {}).get("latency_ms", 0)) for s in spans]
        tokens_in = sum(int((s.attrs or {}).get("tokens_in", 0)) for s in spans)
        tokens_out = sum(int((s.attrs or {}).get("tokens_out", 0)) for s in spans)
        p50, p95 = (0.0, 0.0)
        if len(latencies) >= 2:
            q = quantiles(latencies, n=100)
            p50, p95 = q[49], q[94]
        elif latencies:
            p50 = p95 = latencies[0]

        db.execute(delete(RunMetrics).where(RunMetrics.run_id == run_id))
        db.add(
            RunMetrics(
                run_id=run_id,
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                cost_usd_est=((tokens_in + tokens_out) / 1000) * COST_PER_1K_TOKENS,
                latency_ms_p50=p50,
                latency_ms_p95=p95,
                tool_calls_count=sum(1 for s in spans if s.type == "tool"),
                llm_calls_count=sum(1 for s in spans if s.type == "llm"),
                failures_count=sum(1 for s in spans if s.status == "failed"),
                created_at=datetime.now(timezone.utc),
            )
        )
        db.commit()
    finally:
        db.close()

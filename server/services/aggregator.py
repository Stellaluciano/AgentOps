from __future__ import annotations

import os

from redis import Redis
from rq import Queue

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


def enqueue_aggregation(run_id: str) -> None:
    queue = Queue("agentops", connection=Redis.from_url(REDIS_URL))
    queue.enqueue("worker.jobs.aggregate_run.aggregate_run_metrics", run_id)

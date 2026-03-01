from __future__ import annotations

import os

from redis import Redis
from rq import Worker

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")


def main() -> None:
    conn = Redis.from_url(REDIS_URL)
    worker = Worker(["agentops"], connection=conn)
    worker.work()


if __name__ == "__main__":
    main()

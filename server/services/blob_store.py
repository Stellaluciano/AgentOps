from __future__ import annotations

import gzip
import json
from pathlib import Path


class LocalBlobStore:
    def __init__(self, root: str = "./data/blobs"):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def put_json(self, key: str, data: dict) -> str:
        path = self.root / f"{key}.json.gz"
        with gzip.open(path, "wt", encoding="utf-8") as f:
            json.dump(data, f)
        return str(path)

    def get_json(self, ref: str) -> dict:
        with gzip.open(ref, "rt", encoding="utf-8") as f:
            return json.load(f)

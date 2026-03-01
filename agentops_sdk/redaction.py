from __future__ import annotations

import re
from typing import Any

DEFAULT_PATTERNS = {
    "email": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "phone": re.compile(r"\+?\d[\d\s()-]{7,}\d"),
    "credit_card": re.compile(r"\b(?:\d[ -]*?){13,16}\b"),
}


def redact_value(value: Any, allowlist: set[str] | None = None) -> Any:
    allowlist = allowlist or set()
    if isinstance(value, dict):
        return {k: (v if k in allowlist else redact_value(v, allowlist)) for k, v in value.items()}
    if isinstance(value, list):
        return [redact_value(v, allowlist) for v in value]
    if isinstance(value, str):
        redacted = value
        for label, pattern in DEFAULT_PATTERNS.items():
            redacted = pattern.sub(f"[REDACTED_{label.upper()}]", redacted)
        return redacted
    return value

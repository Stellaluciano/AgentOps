from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class LLMProvider(Protocol):
    def complete(self, prompt: str) -> str: ...


@dataclass
class MockOpenAIAdapter:
    model: str = "gpt-mock-1"

    def complete(self, prompt: str) -> str:
        return f"[{self.model}] Deterministic response for: {prompt[:120]}"

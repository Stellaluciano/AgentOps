from __future__ import annotations

import random

from agentops_sdk.exporters.http import HTTPBatchExporter
from agentops_sdk.providers.openai import MockOpenAIAdapter
from agentops_sdk.trace import TraceClient


def web_search_mock(query: str) -> str:
    return f"Top result for '{query}': AgentOps helps trace agent workflows."


def calculator_mock(expr: str) -> str:
    return str(eval(expr, {"__builtins__": {}}, {}))  # noqa: S307


def retrieval_mock(query: str) -> list[dict[str, str]]:
    return [
        {"id": "doc-1", "text": f"About {query}: observability and replay."},
        {"id": "doc-2", "text": "Evaluation harness can score tasks."},
    ]


def llm_mock(prompt: str) -> str:
    provider = MockOpenAIAdapter()
    return provider.complete(prompt)


def run_demo() -> None:
    exporter = HTTPBatchExporter("http://localhost:8000")
    tracer = TraceClient(exporter=exporter, allowlist={"safe_field"})

    tracer.start_run(project="demo", name="toy-agent", tags={"env": "local"})
    question = random.choice(["What is 2+2?", "How does AgentOps help?"])

    with tracer.span("retrieval", "retrieve_context", attrs={"query": question}):
        docs = retrieval_mock(question)

    with tracer.span("tool", "web_search", attrs={"query": question}):
        web = web_search_mock(question)

    with tracer.span("tool", "calculator", attrs={"expr": "2+2"}):
        calc = calculator_mock("2+2")

    with tracer.span("llm", "generate_answer", attrs={"prompt": question, "tool_io": {"web": web, "calc": calc, "docs": docs}}):
        _answer = llm_mock(f"Q: {question}\nDocs:{docs}\nWeb:{web}\nCalc:{calc}")

    tracer.end_run(status="completed", metadata={"question": question})


if __name__ == "__main__":
    run_demo()

from agentops_sdk.trace import TraceClient


class DummyExporter:
    def __init__(self):
        self.last = None

    def export_events(self, events):
        self.last = events
        return {"accepted": len(events)}


def test_trace_generates_events():
    ex = DummyExporter()
    tc = TraceClient(exporter=ex)
    tc.start_run("p", "n")
    with tc.span("tool", "x", attrs={"email": "a@b.com"}):
        pass
    tc.end_run()
    assert ex.last is not None
    assert any(e["kind"] == "span" for e in ex.last)

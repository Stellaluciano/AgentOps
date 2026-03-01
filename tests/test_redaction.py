from agentops_sdk.redaction import redact_value


def test_redact_email():
    out = redact_value({"msg": "email me at a@b.com"})
    assert "REDACTED_EMAIL" in out["msg"]

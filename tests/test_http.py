"""Preserve the service's HTTP contract with actual TestClient lifespans."""

from __future__ import annotations

from fastapi.testclient import TestClient
from pytest import MonkeyPatch

from virtualmoney.app import create_app


def test_service_http_contract(monkeypatch: MonkeyPatch) -> None:
    application = create_app()

    @application.get("/validate/{item_id}")
    async def validate(item_id: int) -> dict[str, int]:
        return {"item_id": item_id}

    @application.get("/fail")
    async def fail() -> None:
        raise RuntimeError("internal detail must stay private")

    assert not hasattr(application.state, "resources")
    with TestClient(application) as client:
        assert hasattr(application.state, "resources")
        root = client.get("/")
        assert root.status_code == 200 and root.json()["ok"] is True
        document = client.get("/getOpenApi")
        assert document.status_code == 200
        assert document.json() == application.openapi()
        assert document.json()["paths"]["/"]["get"]["operationId"] == "getRoot"
        assert (
            document.json()["paths"]["/getOpenApi"]["get"]["operationId"]
            == "getOpenApi"
        )
        assert "/health/live" not in document.json()["paths"]
        assert client.get("/health/live").status_code == 200
        missing = client.get("/missing")
        assert missing.status_code == 404
        assert missing.json()["error"] == "VIRTUALMONEY_NOT_FOUND"
        invalid = client.get("/validate/not-an-int")
        assert invalid.status_code == 422
        assert invalid.json()["error"] == "VIRTUALMONEY_VALIDATION_ERROR"
        assert client.get("/health/ready").status_code == 200
    assert not hasattr(application.state, "resources")
    with TestClient(application, raise_server_exceptions=False) as client:
        failure = client.get("/fail")
        assert failure.status_code == 500
        assert failure.json()["error"] == "VIRTUALMONEY_INTERNAL_ERROR"
        assert "internal detail" not in failure.text
    assert not hasattr(application.state, "resources")

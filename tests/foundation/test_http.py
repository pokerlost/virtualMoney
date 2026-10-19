"""Managed tests for the HTTP, configuration, and resource ownership contract."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Annotated
from uuid import UUID

import pytest
from fastapi import Body, FastAPI, HTTPException, Request
from fastapi.testclient import TestClient
from httpx import Response
from pydantic import ValidationError

from virtualmoney.app import create_app
from virtualmoney.resources import ApplicationResources, get_resources
from virtualmoney.settings import ServiceSettings

EXPECTED_OPENAPI_PATHS = {"/", "/getOpenApi"}


def assert_error(response: Response, status: int, code: str, message: str) -> None:
    assert response.status_code == status
    assert response.json() == {
        "ok": False,
        "result": None,
        "error": "VIRTUALMONEY_" + code,
        "error_message": message,
        "retry_after": None,
    }


@pytest.fixture(autouse=True)
def isolated_settings(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    monkeypatch.delenv("VIRTUALMONEY_LOGLEVEL", raising=False)
    monkeypatch.delenv("VIRTUALMONEY_LOG_LEVEL", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    logger = logging.getLogger("virtualMoney")
    level = logger.level
    try:
        yield
    finally:
        logger.setLevel(level)


@pytest.fixture
def application() -> FastAPI:
    return create_app()


@pytest.fixture
def client(application: FastAPI) -> Iterator[TestClient]:
    assert not hasattr(application.state, "resources")
    with TestClient(application) as instance:
        assert isinstance(application.state.resources, ApplicationResources)
        yield instance
    assert not hasattr(application.state, "resources")


def test_infrastructure_and_disabled_routes(
    application: FastAPI, client: TestClient
) -> None:
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}
    for path in ("/missing", "/docs", "/redoc", "/openapi.json"):
        assert_error(client.get(path), 404, "NOT_FOUND", "Resource not found")
    assert_error(
        client.post("/health/live"), 405, "METHOD_NOT_ALLOWED", "Method not allowed"
    )
    assert set(application.openapi()["paths"]) == EXPECTED_OPENAPI_PATHS


def test_method_not_allowed_preserves_allow(client: TestClient) -> None:
    response = client.post("/health/live")
    assert response.status_code == 405
    assert "GET" in response.headers["allow"]


@pytest.mark.parametrize(
    ("status", "name", "value"),
    [(401, "WWW-Authenticate", "Bearer"), (503, "Retry-After", "30")],
)
def test_protocol_headers_without_private_details(
    application: FastAPI, client: TestClient, status: int, name: str, value: str
) -> None:
    @application.get("/technicalProtocolError")
    async def fail() -> None:
        raise HTTPException(
            status,
            detail="synthetic-private-value",
            headers={
                name: value,
                "X-Private": "synthetic-private-value",
                "Content-Length": "999",
            },
        )

    response = client.get("/technicalProtocolError")
    assert response.status_code == status
    assert response.headers[name] == value
    assert "x-private" not in response.headers
    assert "synthetic-private-value" not in response.text
    assert int(response.headers["content-length"]) == len(response.content)


@pytest.mark.parametrize("status", [103, 204, 304])
def test_bodyless_http_exception_uses_framework_semantics(
    application: FastAPI, client: TestClient, status: int
) -> None:
    @application.get("/technicalBodyless")
    async def fail() -> None:
        raise HTTPException(status, detail="synthetic-private-value")

    response = client.get("/technicalBodyless")
    assert response.status_code == status
    assert response.content == b""
    assert "content-type" not in response.headers


@pytest.mark.parametrize("incoming", ["probe-123", "a" * 64])
def test_valid_request_id_is_preserved(client: TestClient, incoming: str) -> None:
    response = client.get("/health/live", headers={"X-Request-ID": incoming})
    assert response.headers["X-Request-ID"] == incoming


@pytest.mark.parametrize("incoming", ["", " bad-id", "a" * 65])
def test_invalid_request_id_is_replaced(client: TestClient, incoming: str) -> None:
    response = client.get("/health/live", headers={"X-Request-ID": incoming})
    generated = response.headers["X-Request-ID"]
    assert generated != incoming
    assert str(UUID(generated)) == generated


@pytest.mark.parametrize("alias", ["LOGLEVEL", "LOG_LEVEL"])
def test_settings_aliases(monkeypatch: pytest.MonkeyPatch, alias: str) -> None:
    monkeypatch.setenv("VIRTUALMONEY_" + alias, "DEBUG")
    assert ServiceSettings().log_level == "DEBUG"


def test_settings_validation_hides_input(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VIRTUALMONEY_LOGLEVEL", "synthetic-private-value")
    with pytest.raises(ValidationError) as error:
        ServiceSettings()
    assert "synthetic-private-value" not in str(error.value)


def test_application_resources_are_independent() -> None:
    settings = ServiceSettings(log_level="WARNING")
    first = create_app(settings)
    second = create_app(settings)
    assert not hasattr(first.state, "resources")
    assert not hasattr(second.state, "resources")
    with TestClient(first) as one:
        first_resources = first.state.resources
        with TestClient(second) as two:
            assert first_resources is not second.state.resources
            assert one.get("/health/live").status_code == 200
            assert two.get("/health/live").status_code == 200
        assert not hasattr(second.state, "resources")
        assert first.state.resources is first_resources
    assert not hasattr(first.state, "resources")


def test_resources_require_a_running_lifespan(application: FastAPI) -> None:
    request = Request({"type": "http", "app": application})
    with pytest.raises(RuntimeError, match="not initialized"):
        asyncio.run(get_resources(request))


def test_validation_does_not_echo_input(
    application: FastAPI, client: TestClient, caplog: pytest.LogCaptureFixture
) -> None:
    @application.post("/technicalValidation")
    async def validate(payload: Annotated[int, Body(embed=True)]) -> dict[str, int]:
        return {"payload": payload}

    response = client.post(
        "/technicalValidation", json={"payload": "synthetic-private-value"}
    )
    assert_error(response, 422, "VALIDATION_ERROR", "Request validation failed")
    assert "synthetic-private-value" not in response.text
    assert "synthetic-private-value" not in caplog.text


@pytest.mark.parametrize(
    ("status", "code", "message"),
    [
        (404, "NOT_FOUND", "Resource not found"),
        (405, "METHOD_NOT_ALLOWED", "Method not allowed"),
        (503, "DEPENDENCY_UNAVAILABLE", "Required dependency unavailable"),
        (409, "HTTP_ERROR", "HTTP request failed"),
    ],
)
def test_framework_error_shape(
    application: FastAPI,
    client: TestClient,
    status: int,
    code: str,
    message: str,
) -> None:
    @application.get("/technicalStatus")
    async def fail() -> None:
        raise HTTPException(status, detail="synthetic-private-value")

    response = client.get("/technicalStatus")
    assert_error(response, status, code, message)
    assert "synthetic-private-value" not in response.text


def test_handled_500_redacts_exception(
    application: FastAPI, caplog: pytest.LogCaptureFixture
) -> None:
    @application.get("/technicalFailure")
    async def fail() -> None:
        raise RuntimeError("synthetic-private-value")

    with TestClient(application, raise_server_exceptions=False) as client:
        response = client.get(
            "/technicalFailure", headers={"X-Request-ID": "safe-probe"}
        )
        assert_error(response, 500, "INTERNAL_ERROR", "Internal server error")
        assert response.headers["X-Request-ID"] == "safe-probe"
        assert "synthetic-private-value" not in response.text
    assert "synthetic-private-value" not in caplog.text
    assert not hasattr(application.state, "resources")


def test_unexpected_error_without_correlation_state(application: FastAPI) -> None:
    request = Request({"type": "http", "app": application})
    handler = application.exception_handlers[Exception]
    response = asyncio.run(handler(request, RuntimeError("synthetic-private-value")))
    assert response.status_code == 500
    assert "X-Request-ID" not in response.headers
    assert "synthetic-private-value" not in json.dumps(json.loads(response.body))


def test_import_has_no_settings_or_network_side_effects(tmp_path: Path) -> None:
    environment = os.environ.copy()
    for name in (
        "DATABASE_URL",
        "VIRTUALMONEY_LOGLEVEL",
        "VIRTUALMONEY_LOG_LEVEL",
    ):
        environment.pop(name, None)
    code = """
import socket
def reject_network(*args, **kwargs):
    raise RuntimeError("Network I/O during import")
socket.socket.connect = reject_network
from virtualmoney.app import create_app
assert callable(create_app)
"""
    result = subprocess.run(
        [sys.executable, "-I", "-c", code],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert result.returncode == 0, result.stderr


def test_readiness_tracks_enabled_resources(
    application: FastAPI, client: TestClient
) -> None:
    assert client.get("/health/ready").json() == {"status": "ready"}
    application.state.resources = ApplicationResources(ready=False)
    assert_error(
        client.get("/health/ready"),
        503,
        "DEPENDENCY_UNAVAILABLE",
        "Required dependency unavailable",
    )
    assert client.get("/health/live").status_code == 200

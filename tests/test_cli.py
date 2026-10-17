"""Keep the published operator command bound to the migrated application."""

from __future__ import annotations

from pytest import MonkeyPatch
from typer.testing import CliRunner

from virtualmoney.cli import cli


def test_run_command_keeps_entrypoint(monkeypatch: MonkeyPatch) -> None:
    """The existing command must start the single current FastAPI factory."""
    calls: list[tuple[str, bool, str, int]] = []

    def fake_run(application: str, *, factory: bool, host: str, port: int) -> None:
        calls.append((application, factory, host, port))

    monkeypatch.setattr("virtualmoney.cli.uvicorn.run", fake_run)
    result = CliRunner().invoke(cli, ["run", "--host", "127.0.0.1", "--port", "8123"])

    assert result.exit_code == 0, result.output
    assert calls == [("virtualmoney.app:create_app", True, "127.0.0.1", 8123)]

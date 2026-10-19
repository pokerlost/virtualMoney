"""Local operator entrypoint for the infrastructure foundation."""

from __future__ import annotations

import typer
import uvicorn

cli = typer.Typer(no_args_is_help=True)


@cli.callback()
def main() -> None:
    """Expose the existing `virtualMoney run` command group."""


@cli.command()
def run(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Run the local FastAPI foundation."""
    uvicorn.run("virtualmoney.app:create_app", factory=True, host=host, port=port)

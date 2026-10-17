"""Local operator entrypoint for the infrastructure foundation."""

from __future__ import annotations

import typer
import uvicorn

cli = typer.Typer(no_args_is_help=True)


@cli.command()
def run(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Run the local FastAPI foundation."""
    uvicorn.run("virtualMoney.app:createApp", factory=True, host=host, port=port)

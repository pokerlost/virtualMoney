"""Small Typer interface for local virtualMoney startup."""

from __future__ import annotations

from typing import Annotated

import typer
import uvicorn

from configuration import Settings

cli = typer.Typer(
    name="virtualMoney",
    help="Run the virtualMoney service locally.",
    no_args_is_help=True,
)


@cli.command()
def run(
    host: Annotated[str | None, typer.Option(help="HTTP bind host override.")] = None,
    port: Annotated[
        int | None,
        typer.Option(min=1, max=65535, help="HTTP bind port override."),
    ] = None,
    reload: Annotated[
        bool,
        typer.Option(help="Reload the local server when source files change."),
    ] = False,
) -> None:
    """Start one local Uvicorn development worker."""
    settings = Settings()
    uvicorn.run(
        "api.application:create_app",
        factory=True,
        host=host if host is not None else settings.http.host,
        port=port if port is not None else settings.http.port,
        workers=1,
        reload=reload,
        access_log=False,
    )

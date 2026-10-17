# virtualMoney

A local Pokerlost financial service foundation. The active application exposes infrastructure only; it does not accept money operations or maintain balances. See [SERVICE.md](SERVICE.md) for ownership and migration status.

## 🚀 Run

Python 3.14+ and read access to the pinned private `pypokerlost` source are needed to install. No database or external financial credential is used by this foundation.

```bash
uv sync --locked
uv run --locked virtualMoney run --host 127.0.0.1 --port 8000
```

The existing `virtualMoney run` command starts the same application factory as `uvicorn virtualMoney.app:createApp --factory`. The only registered paths are `GET /`, `GET /getOpenApi`, `/health/live`, and `/health/ready`. The former dotted financial API is [historical reference](docs/history/README.md), not a current route or SDK guarantee.

## 🛠 Development

```bash
uv lock --check
uv run --locked ruff check src
uv run --locked ruff format --check src
uv run --locked mypy
uv build
```

The [foundation architecture](docs/architecture.md) comes from the pinned template; [SERVICE.md](SERVICE.md) owns business boundaries. No new subject tests or CI workflow are enabled. The confirmed source has no historical Alembic revision files. A Docker/Helm deployment target and database schema require a separate review; the old deployment preset is not part of this foundation.

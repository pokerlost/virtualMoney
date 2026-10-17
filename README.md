# virtualMoney

A local Pokerlost financial service foundation. The active application exposes infrastructure only; it does not accept money operations or maintain balances. See [SERVICE.md](SERVICE.md) for ownership and migration status.

## 🚀 Run

Python 3.14+ and local read access to the pinned private `pypokerlost` source are needed to install. The installed wheel includes the SDK as a runtime dependency and needs no adjacent checkout. No database or external financial credential is used by this foundation.

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

Technical CI checks source on PRs without secrets. A trusted push also attempts the pinned private SDK build; it reports a block until the repository-scoped GitHub App secrets are configured. No subject test suite is installed. The [foundation architecture](docs/architecture.md) comes from the pinned template; [SERVICE.md](SERVICE.md) owns business boundaries. The confirmed prior source has no Alembic revision files. A Docker/Helm deployment target and database schema require separate review; the old deployment preset is not part of this foundation.

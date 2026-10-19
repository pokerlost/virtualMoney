# virtualMoney

A local Pokerlost financial service foundation. The active application exposes infrastructure only; it does not accept money operations or maintain balances. See [SERVICE.md](SERVICE.md) for ownership and migration status.

## 🚀 Run

Python 3.14+ and local read access to the pinned private `pypokerlost` source are needed to install. The installed wheel includes the SDK as a runtime dependency and needs no adjacent checkout. No database or external financial credential is used by this foundation.

```bash
uv sync --locked
uv run --locked virtualMoney run --host 127.0.0.1 --port 8000
```

The existing `virtualMoney run` command starts the same application factory as `uvicorn virtualmoney.app:create_app --factory`. The only registered paths are `GET /`, `GET /getOpenApi`, `/health/live`, and `/health/ready`. The former dotted financial API is [historical reference](docs/history/README.md), not a current route or SDK guarantee.

## 🛠 Development

```bash
uv lock --check
uv run --locked ruff check src
uv run --locked ruff format --check src
uv run --locked mypy
uv build
```

Technical CI checks source on PRs without secrets. The pinned private SDK build is manually gated by reviewed SHA and the approved solo-owner/full-SHA admission policy. Run `uv run --locked pytest -q` for HTTP and CLI regression coverage. The [foundation architecture](docs/architecture.md) comes from the pinned template; [SERVICE.md](SERVICE.md) owns business boundaries. The confirmed prior source has no Alembic revision files. The Dockerfile builds this backend with a BuildKit SDK token secret; the managed Helm chart is available, and persistence remains disabled.

## Tested foundation commands

The shared template owns `Makefile`, `tests/foundation/` and `deploy/chart/`. Project-owned tests,
settings, scopes and migration history survive updates. `make test-unit` reports isolated
coverage; `make test` also measures enabled integration before advisory report generation. Missing owned
paths remain visible in the report. `make build image verify` uses the canonical wheel
container graph and requires the separately approved SDK-only BuildKit secret.

`make chart-check chart` validates/packages the shared chart. `make deploy-local` and
`make undeploy-local` operate only the explicit disposable Kind contour. External deployment
requires an approved destination and tested image manifest digest. Private runtime CI requires
a full reviewed SHA and the SDK-only App approval gate; skipped runtime checks do not pass.

## Docker verification

`make source` parses the required frozen lock, checks formatting/lint and compiles source using
public Docker tools without installing the SDK. It does not verify runtime types or tests.
After approved SDK access, `make check build verify image` uses the canonical Docker graph;
provide the short-lived token only with `DOCKER_BUILD_ARGS='--secret id=sdk_token,env=SDK_APP_TOKEN'`.
`check` runs strict static/unit checks once; `verify` freshly tests the installed wheel and any
enabled disposable PostgreSQL profile, with separate `coverage/installed/` reports. `make coverage`
reads current source reports without rerunning tests. Below 100% warns; assertions, types,
build/configuration/access and invalid/stale report errors fail.

Private SDK acceptance follows the [reviewed-source admission guide](.github/docs/sdk-admission.md).
The trusted default-branch workflow uses a separately admitted full source SHA; integrated
commits do not need an open PR. This is the approved solo-owner review model, not independent
environment approval. Ordinary source checks do not establish runtime acceptance.
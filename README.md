# virtualMoney

`virtualMoney` is the PostgreSQL-backed source of truth for internal poker money. It owns assets,
financial accounts, the immutable double-entry ledger, materialized balances, holds, pooled table
escrow, BuyIn/ReBuy/CashOut, rake, full compensation, and financial history. Money is represented
as Python `int` and PostgreSQL `BIGINT` integer minimal units.

Poker Server owns game state, pots, final stacks, and rake calculation. It supplies authoritative
amounts; `virtualMoney` validates financial invariants and persists their effects atomically. The
service deliberately has no Redis, NoSQL, blockchain, wallet, message broker, or local
authentication dependency.

## Architecture

```text
FastAPI action router
  -> feature-local Handler provider
  -> immutable Command or Query
  -> operation Handler and shared financial service
      -> SQLAlchemy Entity Repository -> PostgreSQL -> ORM models
      -> SQLAlchemy Read Query Adapter -> PostgreSQL -> Pydantic projections
```

Pydantic v2 owns immutable Commands, Queries, structured application results, domain value models,
pagination values, persistence read projections, API schemas, and Settings. Persisted internal
entities remain typed SQLAlchemy ORM models, and runtime resources remain normal explicit classes.
Reusable semantic validation lives under `domain/types/`; there is no duplicate ORM-to-domain
mapping layer. The composition root owns runtime configuration, resources, exception handlers,
routes, and instrumentation.

The main source layout is:

```text
app/
  api/
    dependencies/              # central resource/session/settings dependencies
    errors/                    # application, database, validation, unexpected handlers
    routers/<feature>/         # base router, action subrouters, local providers
    schemas/
      base/                    # shared Pydantic API bases
      requests/                # HTTP request bodies
      orm/                     # direct entity output contracts
      responses/               # calculated and composite results
  application/<feature>/<operation>/ # immutable Command/Query and Handler
  configuration/              # logical settings groups
  domain/
    enums/                     # one enum per file
    errors/                    # feature-owned invariant errors
    types/                     # shared validated semantic primitives
    money.py and value_model.py # financial bounds and immutable model base
  observability/               # Logfire configuration and instrumentation
  persistence/
    database/                  # Base, mixins, result readers, session, and ORM models
    projections/               # immutable Pydantic SQL read shapes
    queries/                   # optimized read projection adapters
    repositories/              # entity and aggregate persistence adapters
```

`app/` is the Python source root, not an import namespace. Local processes use `PYTHONPATH=app`,
and application imports start with `api`, `application`, `configuration`, `domain`,
`observability`, or `persistence`. Docker configures `PYTHONPATH=/service/app`.
Every package directory below that source root has an `__init__.py`. Facades expose only symbols
with real external consumers, and application feature facades expose public Commands, Queries,
and Handlers. Same-package imports may be relative, but parent-climbing `from ..` imports are
forbidden; architectural package crossings are absolute. Code imports FastAPI public symbols
instead of equivalent Starlette exports and imports specific symbols instead of one-use modules.

## HTTP convention

The API is intentionally RPC-like. Every operation or query requiring input uses `POST` with one
documented Pydantic JSON body. Only parameterless process endpoints use `GET`. Business resource
IDs never live in path parameters, and operation IDs never live in headers. Paths use camelCase;
Python identifiers use snake_case.

| Method | Path                                   | Purpose                                     |
|--------|----------------------------------------|---------------------------------------------|
| `GET`  | `/`                                    | Service identity                            |
| `POST` | `/assets.getAsset`                     | Get an asset by ID                          |
| `POST` | `/assets.getAssetByCode`               | Get an asset by code                        |
| `POST` | `/accounts.createAccount`              | Create an account idempotently              |
| `POST` | `/accounts.getAccount`                 | Get an account                              |
| `POST` | `/accounts.getBalance`                 | Get posted, held, and available balances    |
| `POST` | `/accounts.getFinancialHistory`        | Get cursor-paginated account history        |
| `POST` | `/ledger.postTransaction`              | Post a balanced adjustment                  |
| `POST` | `/ledger.getTransaction`               | Get an immutable ledger transaction         |
| `POST` | `/ledger.reverseTransaction`           | Fully reverse a ledger transaction          |
| `POST` | `/holds.reserveHold`                   | Reserve funds in full                       |
| `POST` | `/holds.getHold`                       | Get a hold                                  |
| `POST` | `/holds.releaseHold`                   | Release an active hold in full              |
| `POST` | `/holds.captureHold`                   | Capture an active hold in full              |
| `POST` | `/tablePositions.buyIn`                | Capture a hold and open a position          |
| `POST` | `/tablePositions.reBuy`                | Capture another hold into an open position  |
| `POST` | `/tablePositions.cashOut`              | Return the final stack and close a position |
| `POST` | `/tablePositions.getPosition`          | Get a durable position                      |
| `POST` | `/tablePositions.getOperations`        | Get cursor-paginated position operations    |
| `POST` | `/rake.chargeRake`                     | Transfer rake from table escrow             |
| `POST` | `/financialOperations.getOperation`    | Get a source-discriminated operation        |
| `POST` | `/financialOperations.refundOperation` | Fully compensate a ledger-backed operation  |

Every response uses one envelope. The HTTP status is not duplicated in JSON:

```json
{
  "ok": true,
  "result": {}
}
```

```json
{
  "ok": false,
  "result": null,
  "error": "IDEMPOTENCY_CONFLICT",
  "errorMessage": "..."
}
```

Action handlers return a raw dictionary containing the typed result and let their concrete FastAPI
`response_model` validate, filter, and serialize it; they do not call `model_dump()` solely for
transport serialization. Central exception handlers alone construct error responses.

## Pydantic schema boundaries

`api/schemas/requests/` contains only HTTP body models. They use camelCase aliases, reject unknown
input, document fields, and may perform a trivial `to_command()` mapping with no orchestration.

`api/schemas/orm/` contains direct entity output contracts such as `AccountSchema`, `HoldSchema`,
and `PlayerTablePositionSchema`. Their shared base enables `from_attributes=True`; they are not
SQLAlchemy models.

`api/schemas/responses/` contains projections and composites whose meaning is not a single entity:
balance details, history rows, source-discriminated operation variants, and generic pagination.
Application models stay with their owning feature and have no transport aliases.

Reusable semantic types under `domain/types/` serve API, application, domain, and persistence
boundaries without duplicate validators. `NonNilUUID` validates entity identifiers, `OperationId`
gives business operation IDs distinct semantics, money-minor types enforce BIGINT bounds and sign
rules, and focused types cover asset codes, references, timestamps, descriptions, and
fingerprints. `api/types/` retains only transport-specific typing helpers.

Requests transfer explicit fields into separate immutable Pydantic Commands or Queries. Internal
structured models inherit the alias-free `ValueModel`; database projections inherit the frozen
`ProjectionModel`. SQLAlchemy mapped entities and runtime resource/service objects do not use
Pydantic.

## Dependency injection and transaction lifecycle

Each feature router has a small `dependencies.py` that constructs its Handlers, entity
repositories, and read query adapters explicitly. There is no global use-case registry and no
dependency alias for each endpoint.

One function-scoped FastAPI yield dependency owns the request transaction:

```python
async def get_database_session(resources: ApplicationResourcesDep) -> AsyncIterator[AsyncSession]:
    async with resources.session_factory.begin() as session:
        yield session


type DatabaseSession = Annotated[
    AsyncSession,
    Depends(get_database_session, scope="function"),
]
```

The lifecycle is therefore:

```text
create session -> BEGIN -> Handler/services/repositories/queries -> dependency exits
                                                      -> COMMIT on success
                                                      -> ROLLBACK on exception
                                                      -> close session
                                                      -> send HTTP response
```

FastAPI 0.121 or newer is required for the function-scoped yield dependency. Handlers, services,
repositories, and query adapters never call `commit()` or `rollback()`. All persistence
adapters created for a request share one `AsyncSession`; the former Unit of Work wrapper has been
removed. Expected exceptions leave the handler, allowing SQLAlchemy's context manager to roll back
before the API handler renders an error. Database `OperationalError` and pool timeout are mapped
centrally to `503`; other SQLAlchemy failures are rendered as safe `500` responses without SQL,
constraint details, DSNs, or driver messages.

Returned ORM entities and persistence projections must already have every response field available
because response serialization cannot perform lazy SQL after transaction cleanup. Repositories
use explicit eager loading for required relationships, while query adapters return complete typed
projections. The session factory uses `expire_on_commit=False` for safe scalar access.

## Persistence adapters and financial primitives

Handlers and shared services receive concrete constructor-injected `SQLAlchemy...Repository`
adapters for entity persistence and `SQLAlchemy...Query` adapters for optimized read projections.
Both use typed SQLAlchemy 2.x statements and the same request session, make no HTTP decisions, and
never finish transactions.

`SQLAlchemyRepository` owns only the request session and typed scalar/projection execution.
`SQLAlchemyEntityRepository[T]` adds the common UUID `get_by_id()` for standard `UUIDModel`
entities; `AccountBalanceModel` uses the general base because `account_id` is its primary key.
Entity repository reads return ORM models or deterministic lists of ORM models. Empty collection
reads return `[]`; when business logic needs keyed lookup, the application indexes those rows.

All scalar extraction, including ORM entities and DML `RETURNING` values, goes through
`SQLAlchemyScalarResultReader[T]`. Explicitly labeled mapping rows are validated with Pydantic
`TypeAdapter` through `SQLAlchemyProjectionResultReader[T]`. Both readers expose only `one()`,
`one_or_none()`, and `all()`. Concrete repositories and query adapters never call SQLAlchemy
scalar, mapping, or tuple extraction APIs directly. Repository writes use explicit DML and
`RETURNING`; normal write paths do not use `AsyncSession.add()`, `add_all()`, `flush()`, or
`refresh()`, and write methods do not hide a read-after-write.

Account history, table-position operations, and cross-source operation lookup use three focused
query adapters returning immutable persistence projections. Financial-operation lookup returns a
discriminated union with `source` values `LEDGER`, `HOLD`, `TABLE_MONEY`, `RAKE`, or `REFUND`; each
variant preserves its native operation enum instead of using persistence-level enum mapper
functions.

The financial invariants are:

- every ledger transaction has at least two non-zero same-asset entries summing to zero;
- posted journals and entries are immutable;
- corrections are new complete `REVERSAL` transactions;
- posted balance changes with ledger posting in the same transaction;
- held balance changes with immutable hold audit in the same transaction;
- available balance is derived as `postedBalanceMinor - heldBalanceMinor`;
- holds support only full `ACTIVE -> RELEASED` or `ACTIVE -> CAPTURED` transitions;
- hold capture posts one immutable `HOLD_CAPTURE` transfer;
- internal ledger references use `LedgerReferenceType`, while custom ADJUSTMENT references remain
  validated open namespaces;
- BuyIn/ReBuy capture into pooled table escrow and CashOut returns the authoritative final stack;
- service-provisioned TABLE_ESCROW and RAKE account IDs are generated by PostgreSQL and identified
  logically by ownership/type/asset uniqueness rather than deterministic UUID namespaces;
- USER and TABLE accounts have a non-null owner UUID; SYSTEM accounts have `owner_id = NULL`;
- each asset has at most one system-owned `RAKE` account and one system-owned `TREASURY` account;
- rake moves a positive BIGINT-safe amount from table escrow to the rake account;
- compensation reverses a complete ledger-backed operation and appends immutable refund audit;
- a stable operation ID plus canonical business payload provides exact replay or a conflict;
- unique constraints remain the final protection for concurrent idempotency races.

Restart recovery relies only on PostgreSQL. Balance reconciliation reports projection mismatches
and never silently repairs or bypasses the ledger.

## Pagination

Immutable history centralizes cursor, policy, and response values without a generic query
framework. A focused persistence helper builds the shared descending timestamp-and-UUID predicate;
each query adapter still chooses its columns, ordering, and limit. Requests contain a nested body
value such as:

```json
{
  "accountId": "0198...",
  "pagination": {
    "cursor": null,
    "limit": 50
  }
}
```

Responses contain `items` and `nextCursor`. The opaque, canonical URL-safe cursor represents a UTC
timestamp and UUID. Ordering is descending and server-controlled; limits are validated against
`PaginationSettings` (default 50, maximum 100 by default). Production history never uses OFFSET
or unbounded materialization.

## Configuration and CLI

`Settings(BaseSettings)` is the single environment-loading root and assembles immutable groups
for application, database, HTTP, pagination, and Logfire. Nested groups share `SettingsModel`.
Pydantic Settings loads nested `VIRTUALMONEY_` environment variables at the CLI/composition
boundary; there are no scattered environment reads or import-time settings instances.
`LogfireSettings.minimum_level` accepts Logfire levels directly; no application log-level enum or
conversion layer exists.

```bash
cp .env.example .env
PYTHONPATH=app uv run python -m cli run
PYTHONPATH=app uv run python -m cli run --host 0.0.0.0 --port 8000 --reload
```

The installed project script exposes only `run`. Uvicorn is the local development runner; Gunicorn with
`uvicorn_worker.UvicornWorker` is the production process manager.

## Logfire

Pydantic Logfire is the only application observability implementation. Exception handlers pass
exception objects through `_exc_info` so Logfire owns type, message, and traceback capture. The composition root
configures it once, instruments FastAPI once, and instruments the concrete async SQLAlchemy engine
once. FastAPI instrumentation records route timing and status but drops parsed endpoint arguments,
does not capture request headers, and does not record request bodies. Scrubbing patterns cover
credentials, authorization values, tokens, DSNs, database URLs, and raw financial payload labels.

Remote export is disabled by default. Enable it with
`VIRTUALMONEY_LOGFIRE__SEND_TO_LOGFIRE=true` and provide credentials through Logfire's standard
environment configuration or a Kubernetes Secret. Never put a token in repository values.
Set local verbosity directly with `VIRTUALMONEY_LOGFIRE__MINIMUM_LEVEL=info` or another supported
Logfire level.

## Authentication boundary

The service currently implements no authentication or authorization. All internal endpoints are
unauthenticated and require network isolation or a trusted gateway. Token format, transport, and
introspection remain undefined until the separate Auth Service contract is designed. See
[Future Auth Service Interaction](docs/auth-service.md); no unused auth ports or adapters exist in
the codebase.

## Alembic

Migrations are operator-run and never execute during lifespan or container startup:

```bash
PYTHONPATH=app \
VIRTUALMONEY_DATABASE__URL='postgresql+asyncpg://user:password@host/database' \
uv run alembic upgrade head
```

Revision `20260817_0007` removes obsolete local-auth `actor_service` columns and their constraints
from ledger, hold, table-money, rake, and refund operation records. Its downgrade is intentionally
irreversible because removed identity text cannot be recovered without inventing audit data.
Revision `20260819_0008` migrates SYSTEM accounts to `owner_id = NULL`, adds one-TREASURY-per-asset
partial uniqueness, and refuses downgrade when restoring the old shape would require a fake owner.

## Docker

The production image uses Python 3.12, `PYTHONPATH=/service/app`, a non-root UID/GID, runtime-only
dependencies, no embedded `.env` or secrets, no reload, and no migration-on-startup behavior.

```bash
docker build --tag virtualmoney:local .
docker run --rm --name virtualmoney \
  --env VIRTUALMONEY_DATABASE__URL='postgresql+asyncpg://user:password@host/database' \
  --publish 8000:8000 \
  virtualmoney:local
```

Run Alembic separately before rolling out the application image.

## Helm and kind

The logical service name is exactly `virtualMoney`. Helm chart and Kubernetes DNS identifiers use
the unavoidable lowercase form `virtualmoney`; `virtual-money` and `virtual_money` are not active
deployment names. The chart lives at `deploy/helm/virtualmoney/` and expects database credentials
from an existing Secret. It installs no PostgreSQL, Redis, Auth Service secret, or migration job.

Both liveness and readiness use the process-only `/` endpoint. There is no database probe or
readiness checker.

```bash
kind create cluster --name virtualmoney
kind load docker-image virtualmoney:local --name virtualmoney
kubectl create namespace virtualmoney
kubectl -n virtualmoney create secret generic virtualmoney-database \
  --from-literal=DATABASE_URL='postgresql+asyncpg://user:password@external-host/database'
helm upgrade --install virtualmoney deploy/helm/virtualmoney \
  --namespace virtualmoney \
  --values deploy/helm/virtualmoney/values-kind.yaml
```

The database must be reachable from the cluster; the chart deliberately does not provision it.

## Known limitations

- Internal endpoints are unauthenticated until the external Auth Service/gateway contract exists.
- Network policy, rate limiting, backups, PITR, and migration orchestration are platform concerns.
- Poker Server owns game results, final stacks, and rake calculation.
- Holds and refunds are full-only; holds do not expire automatically.
- There is no message broker, distributed worker, or automatic reconciliation repair.
- `/` proves only that the application process can serve HTTP, not PostgreSQL availability.
- Tests, fixtures, coverage, and CI/CD belong to another stage and are not included here.

See [Platform RPC API Standard](docs/api-standard.md) for the stable OpenAPI and future SDK contract.

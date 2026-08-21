# virtualMoney Repository Rules

## Communication and repository language

- Communicate with the repository user in Russian.
- Keep repository-owned documentation, comments, docstrings, log messages, client-facing
  messages, settings descriptions, and OpenAPI text in English.
- Use concise PEP/reStructuredText-style docstrings. Do not use Google-style `Args:`, `Returns:`,
  or `Raises:` sections, and do not add docstrings that only repeat a symbol name.

## Scope and stack

- `virtualMoney` is the PostgreSQL-backed source of truth for internal poker assets, accounts,
  immutable double-entry ledger entries, balances, holds, table escrow, BuyIn/ReBuy/CashOut,
  rake, full compensation, and financial history.
- Use Python 3.12 or newer, FastAPI, Pydantic v2, Pydantic Settings, SQLAlchemy 2.x async ORM,
  asyncpg, PostgreSQL, Alembic, Typer, Logfire, Docker, Helm, and kind.
- Redis, NoSQL, blockchain, crypto wallets, another ORM, raw-SQL architecture rewrites, message
  brokers, Celery, and hidden infrastructure dependencies are prohibited.
- Keep every change within the requested task. Do not perform unrelated refactoring, destructive
  Git operations, or `git push` unless the user explicitly asks for it.

## Python conventions

- Support Python 3.12 and newer. Ruff targets `py312`; mypy targets Python 3.12.
- The maximum line length is 99. Ruff Formatter is the only formatter.
- Use strict typing and modern syntax where it improves clarity. Avoid `Any`, broad `cast()`,
  broad type ignores, and reflection for fields known at design time.
- Do not use `setattr`, `getattr`, `vars`, `__dict__`, or reflection-based construction when fields
  are known.
- Use `__all__` primarily in package `__init__.py` facades. Leaf modules normally omit it; every
  intentional `__all__` remains a tuple, including the single-item form.
- Choose collections by meaning: `list` for ordered materialization, `set` for uniqueness,
  `frozenset` for immutable uniqueness, and `tuple` only for fixed or immutable sequences or
  library contracts.
- Do not create large mutable structured globals or generic registry/helper frameworks.

## Source root and imports

- `app/` is the Python source root, not an import namespace.
- Local commands use `PYTHONPATH=app`; containers use `PYTHONPATH=/service/app`.
- Import `from api...`, `from application...`, `from configuration...`, `from domain...`,
  `from observability...`, or `from persistence...`; never import `app.*`.
- Every package directory below the `app/` source root contains `__init__.py`; `app/` itself is
  not a package or import namespace.
- Prefer FastAPI public imports over Starlette equivalents whenever FastAPI exposes the symbol.
- Import the specific symbol used instead of a module namespace accessed for one attribute.
- Relative imports may stay within the current package or address its sibling/child modules.
  Parent-climbing `from ..` imports are forbidden; use an absolute architectural package import.
- Imports crossing top-level architectural packages remain absolute.
- A package facade exports only symbols with real external consumers. Application feature facades
  export their public Commands, Queries, and Handlers; root architecture facades remain minimal.
- Never mutate `sys.path` from project code.

## Architecture and application layer

The dependency direction is:

```text
api -> application -> persistence -> domain
configuration/observability -> composition root
```

- Organize `application/` by business feature, not by global command/DTO/query/use-case buckets.
- Keep application input/output models inside the feature that owns them.
- Keep services only when behavior is genuinely reused by multiple use cases. Do not create a
  giant financial service or one-method wrapper packages.
- Domain code owns enums, meaningful constants, reusable semantic Pydantic types, and validated
  value models that are shared across transport and application boundaries.
- SQLAlchemy ORM models are the persisted internal entity representation; do not recreate matching domain entities.
- Do not create service locators, generic repository containers, or duplicate architectural
  styles.

## HTTP API

- Use `POST` for every parameterized business command or query. Use `GET` only for handlers that
  require no request parameters or body.
- Do not use `PUT`, `PATCH`, or `DELETE`.
- Do not use project-owned business `Header` or `Path` parameters. Business identifiers and
  operation IDs belong in one explicit Pydantic request body.
- Use `Query` only as a documented, deliberate exception when it is clearly the best HTTP form.
- Multi-word paths use camelCase; Python identifiers remain snake_case.
- Every route decorator puts `path=` first and declares a concrete `response_model`,
  `status_code`, English `summary`, English `description`, stable `operation_id`, `responses`, and
  a logical tag.
- Use exactly one envelope: `ApplicationResponse[T]` with `ok`, `result`, `error`, and
  `error_message`. Do not put an HTTP status in the JSON body.
- Ordinary handlers return raw dictionaries such as `{"ok": True, "result": result}`. Do not add
  success/error response factories or use `JSONResponse` in ordinary handlers.
- Do not call `.model_validate()` or `.model_dump()` in a handler solely for output serialization.
  Return the typed result inside the raw envelope and let the declared response model serialize it.

## Router architecture and dependency injection

- One router package represents one logical API area.
- Its `router.py` owns the tag and includes action subrouters such as `create.py`,
  `get.py`, or `release.py`.
- Base routers import each child `router` symbol explicitly with a descriptive `_router` alias;
  they do not import whole action modules solely to access `.router`.
- Keep feature-local use-case providers in that router package's `dependencies.py`.
- Do not centralize every repository/use-case dependency in a giant global module and do not
  create one-use named dependency aliases.
- One central database-session dependency is expected. All repositories for one request receive
  that same session.
- Routers depend on use cases, never on `AsyncSession`, SQLAlchemy statements, or persistence
  decisions.

## Pydantic models and public schemas

- Keep HTTP request models under `api/schemas/requests/`, direct entity output schemas under
  `api/schemas/orm/`, and calculated/composite results under `api/schemas/responses/`.
- Request models use camelCase aliases, forbid unknown input, and own transport documentation.
- ORM schemas inherit `from_attributes=True` from their shared base.
- Keep HTTP Request, ORM Schema, and custom Response models separate. Application Commands,
  Queries, structured results, pagination values, and domain value objects are immutable Pydantic
  v2 models without transport aliases.
- Use one small immutable internal Pydantic base for application/domain value models and one small
  immutable persistence projection base. Do not create several equivalent bases.
- SQLAlchemy mapped entities remain SQLAlchemy classes. Runtime resources and service objects are
  normal explicit classes; do not make either category Pydantic merely for convenience.
- Avoid dataclass validation boilerplate and manual `__post_init__` validation. Put reusable
  primitive validation in semantic Pydantic types and keep database-state rules in handlers or
  services.
- Prefer one public request, response, ORM schema, application model, semantic type, or enum per
  file. Use `__init__.py` only for intentional re-exports.
- Reuse semantic validated types such as `NonNilUUID`, `OperationId`, and money-minor types rather
  than repeating validators across models.
- Keep keyset pagination input, cursor, policy, and response shapes centralized.

## Database transactions

- One HTTP request owns one PostgreSQL transaction through `async_sessionmaker.begin()`.
- The FastAPI yield dependency uses `Depends(..., scope="function")`, so commit or rollback
  completes before the response is sent.
- Do not manually call `commit()` or `rollback()` in use cases or repositories.
- Do not reintroduce a Unit of Work transaction wrapper or a repository mega-container.
- Internal posting, capture, projection, and reversal services use repositories sharing the
  request session. They never open or finish transactions.
- Keep `expire_on_commit=False` when response scalar access after dependency cleanup requires it.
- Returned ORM objects must not require lazy I/O during response serialization; eager-load or use
  typed projections when relationships are needed.
- Do not maintain hardcoded SQLSTATE classifications or parse database exception text.

## Errors

- Application errors inherit a small transport-independent semantic category: not found,
  conflict, invalid operation, or integrity.
- Split application and domain errors by feature; do not recreate giant exception modules.
- Split API exception handling by category: application, database, validation, and unexpected.
- Map SQLAlchemy exception classes centrally. Never expose SQL, DSNs, driver messages,
  constraint names, or internal exception strings to clients.
- Let exceptions leave the database dependency so SQLAlchemy owns rollback.

## Enums

- Keep one domain enum per file under `domain/enums/` and intentionally re-export active enums
  from `domain/enums/__init__.py`.
- Do not recreate a monolithic `domain/enums.py`.
- Do not put free enum-to-enum normalization helpers in persistence. Preserve native source enums
  in source-discriminated projections or make a genuine mapping structural to its owning model.
- Platform-owned ledger reference namespaces use `LedgerReferenceType`; internal business logic
  has no magic reference strings. Validated custom low-level ADJUSTMENT namespaces remain open.

## Repositories and persistence

- Application handlers and services use constructor-injected concrete entity repositories from
  `persistence/repositories/` and read adapters from `persistence/queries/`. Ceremonial repository
  Protocols are forbidden.
- SQLAlchemy adapters receive an `AsyncSession`, use typed SQLAlchemy 2.x ORM and `select()`, and
  never import FastAPI, open transactions, commit, rollback, or make business decisions.
- `persistence/repositories/` contains only entity or aggregate persistence adapters. Entity reads
  return ORM models, optional ORM models, or lists of ORM models; repositories never return
  Pydantic projections, API schemas, raw dictionaries, `RowMapping`, or dict-indexed entities.
- Repository collection reads return deterministic lists and use `[]` for an empty collection.
  Application code may index those ORM rows when business validation needs keyed lookup.
- Complex joins, aggregation, history, and other SQL read projections belong to focused adapters
  under `persistence/queries/`. Query adapters return immutable typed Pydantic projections, never
  raw dictionaries, `RowMapping`, tuples, or ORM entity dictionaries.
- Every entity repository inherits `SQLAlchemyRepository`; repositories for standard `UUIDModel`
  entities inherit `SQLAlchemyEntityRepository[ModelT]` and share its typed `get_by_id()`.
  Non-standard-key entities such as `AccountBalanceModel` inherit the general base.
- Keep the repository bases small: they own only the request session, typed scalar/projection
  execution, and standard UUID lookup. Generic CRUD, filters, sorting, mutations, and business
  errors do not belong in the bases.
- `SQLAlchemyScalarResultReader[ResultT]` owns all scalar extraction and exposes only `one()`,
  `one_or_none()`, and `all()`; `all()` returns `list[ResultT]`.
- `SQLAlchemyProjectionResultReader[ProjectionT]` owns all labeled mapping-row extraction, uses
  Pydantic `TypeAdapter`, and exposes only `one()`, `one_or_none()`, and `all()`.
- Concrete repositories and query adapters never call SQLAlchemy `scalar*()`, `scalars()`,
  `mappings()`, or `tuples()` extraction APIs directly.
- Preserve deterministic lock ordering, row locks, PostgreSQL `ON CONFLICT`, and database
  constraints selected for actual financial races.
- Repository writes use explicit DML plus `RETURNING` through the result readers. Do not use
  `AsyncSession.add()`, `add_all()`, `flush()`, or `refresh()` in normal write paths.
- A write returns the ORM row or scalar from that same statement, a natural affected value, or
  `None` for no row. It does not hide a read-after-write; conflict recovery reads stay explicit in
  application orchestration.
- Dictionaries required by FastAPI or OpenAPI metadata are valid at the API composition boundary;
  the prohibition on dictionary results applies to public persistence contracts.
- Schema changes use new deterministic Alembic revisions. Never rewrite old revisions or run
  migrations during application startup.

## SQLAlchemy ORM

- SQLAlchemy infrastructure lives under `persistence/database`; Base, meaningful mixins, and each
  ORM model have focused modules and relative package facades.
- Ordinary UUID entities inherit `UUIDModel`. Use `CreatedAtMixin`, `TimestampMixin`, and
  `OperationIdentityMixin` only where their full repeated persistence structure applies.
- ORM models own mappings, relationships, and database constraints but no Active Record access.
- Add typed relationships where they clarify the used object graph. Relationships use an explicit
  no-hidden-I/O policy such as `lazy="raise"`; use explicit `foreign_keys` for multiple links to
  the same table and eager-load relationships required after request cleanup.
- Keep database financial constraints even when Pydantic validates input first. Metadata-only
  refactors need no migration; real schema changes require a new deterministic revision.
- Database-generated UUIDs plus logical uniqueness express service-provisioned TABLE_ESCROW and
  RAKE identity. Do not use deterministic UUID namespaces or fabricated system owner UUIDs; SYSTEM
  accounts have `owner_id = NULL`, while USER and TABLE ownership remains non-null.

## Financial invariants

- Money is Python `int` and PostgreSQL `BIGINT` in minimal units. Floating-point money is
  prohibited.
- The ledger is immutable double-entry. Every posted transaction has at least two non-zero,
  same-asset entries whose sum is zero.
- Corrections create full reversal transactions; posted transactions and entries are never edited
  or deleted.
- Posted and held balance projections change atomically with their authoritative ledger or hold
  audit. Available balance is derived as posted minus held.
- Holds are full-only `ACTIVE`, `RELEASED`, or `CAPTURED`. Capture posts exactly one immutable
  `HOLD_CAPTURE` transfer.
- Table escrow is a dedicated pooled `TABLE_ESCROW` account. BuyIn/ReBuy capture holds; CashOut
  returns the authoritative final stack and closes the durable position.
- Each asset has at most one system-owned `RAKE` account. Rake moves funds from table escrow to
  that account after all state, funds, asset, BIGINT, and idempotency checks.
- Full compensation appends a `REVERSAL` and immutable refund audit without rewriting prior
  lifecycle history.
- Every state-changing operation has a stable `operation_id`. Exact semantic replay is harmless;
  reuse with another payload is an idempotency conflict.
- Financial history uses bounded descending keyset pagination with an opaque timestamp-and-UUID
  cursor, never unbounded results or OFFSET as the production model.
- The repeated descending timestamp-and-UUID SQL predicate lives in one focused persistence
  helper; each query adapter still owns its columns, ordering, and limit.

## Authentication boundary

- `virtualMoney` contains no authentication or authorization implementation.
- Do not add JWT/Bearer parsing, API keys, token scopes, auth middleware, local principals,
  hardcoded credentials, development tokens, or fake administrators.
- A future external Auth Service owns token issuance and permissions. Until its contract exists,
  document the boundary only; do not add dead ports, adapters, or models.
- Current internal endpoints are unauthenticated and must not claim to provide access security.

## Observability

- Use Pydantic Logfire as the single observability implementation.
- Configure Logfire once and instrument FastAPI and the concrete SQLAlchemy engine once at the
  composition boundary.
- Keep telemetry privacy-safe: do not capture request bodies, endpoint arguments, credentials,
  tokens, DSNs, or raw financial payloads.
- Use safe identifiers and structured spans/events for financial diagnostics. Do not recreate a
  custom JSON logger, ContextVar framework, or OpenTelemetry propagation layer.
- `LogfireSettings.minimum_level` uses values accepted directly by Logfire. Do not recreate a
  `LogLevel` enum or a `to_logfire_level()` conversion. Pass exception objects through `_exc_info`
  without manual exception-type metadata.

## Settings, CLI, and lifespan

- Split settings into logical Pydantic models for application, database, HTTP, pagination, and
  Logfire configuration.
- Keep one root `Settings(BaseSettings)` for environment loading; nested groups inherit the shared
  `SettingsModel`. Logfire owns its minimum level, pagination owns its limits, and Gunicorn process
  settings do not belong in application settings.
- Load `Settings` only at the composition or CLI boundary. Do not instantiate settings at module
  import, scatter environment reads, call `load_dotenv`, or render secrets.
- Typer is a small operator layer only for `run`; it is not runtime
  configuration storage.
- Lifespan creates the engine and session factory, exposes minimal typed resources, and disposes
  the engine after `yield`. It does not migrate, authenticate, query readiness, rebuild state, or
  start unmanaged workers.

## Health and deployment

- Keep only parameterless `GET /`; it performs no database access.
- Kubernetes liveness and readiness both use `/`.
- Do not add a database readiness checker.
- The logical service name is `virtualMoney`; Kubernetes/Helm identifiers use `virtualmoney`.
- Docker uses Gunicorn with `uvicorn_worker.UvicornWorker`; Uvicorn is local-only.

## Final architecture additions

- Every maintained project-owned Python module uses `from __future__ import annotations`; Python
  3.12+, 99 characters, English repository documentation, and canonical acronym spelling such as
  `SQLAlchemy`, `API`, `HTTP`, and `UUID` are mandatory.
- RPC methods use dotted camelCase paths, stable `<resource>_<operation_snake_case>` operation IDs,
  one Request body for parameterized methods, and GET only for parameterless methods.
- Handlers return multiline raw dictionaries in `ApplicationResponse[T]`. Do not add response
  helpers or serialization-only `.model_validate()` calls.
- Application packages are operation-oriented Command/Query + Handler modules. Shared services
  require genuine reuse; giant DTO, model, service, registry, or dependency buckets are forbidden.
- `DatabaseSession` uses function-scoped `Depends` and `session_factory.begin()`. Feature-local
  providers compose handlers and all repositories in one request share that session.
- Errors use semantic categories and focused feature files. API error handlers may instantiate
  `JSONResponse` directly. SQLSTATE lists, exception-string parsing, `_json_response`, and
  `del request` patterns are forbidden.
- Authentication remains external. Typer exposes only `run`; production uses Gunicorn and
  `uvicorn_worker.UvicornWorker`.
- OpenAPI is the future SDK contract. Paths, operation IDs, Request/Result names, JSON fields,
  requiredness, discriminators, and error meanings are stable. Follow `docs/api-standard.md`.
- Do not add an abstraction unless it has an independent responsibility. Approved shared
  abstractions include `ApplicationResponse[T]`, `ValueModel`, `ProjectionModel`,
  `SQLAlchemyRepository`, `SQLAlchemyEntityRepository[T]`,
  `SQLAlchemyScalarResultReader[T]`, and `SQLAlchemyProjectionResultReader[T]`.

## Tests, CI, and completion discipline

- Tests, fixtures, coverage, and CI/CD are not implemented in this repository stage. Do not add
  or modify them unless the user explicitly requests it.
- Preserve unrelated user changes and inspect the complete final diff.
- Never invent test, coverage, migration, Docker, Helm, platform, or compatibility results.
- Report failed or unavailable commands, assumptions, known limitations, checks not run, and
  exact manual verification commands.

## Absolute final typing and persistence rules

- Use Python 3.12 PEP 695 generic syntax everywhere possible. `ApplicationResponse` is the sole
  compatibility exception and uses `typing_extensions.TypeVar(default=None)` because native
  generic defaults require Python 3.13.
- Bare `ApplicationResponse` represents an empty result. `ApplicationResponse[None]` is forbidden.
- Only `ORMSchema` enables `from_attributes=True`; `APIModel`, `RequestModel`, and `ResponseModel`
  must not pretend to be ORM schemas.
- `SQLAlchemyRepository` has no generic write methods; it owns the request session and typed
  `_read_scalar`/`_read_projection` execution. `SQLAlchemyEntityRepository[T]` alone adds standard
  UUID `get_by_id`. `SQLAlchemyScalarResultReader[T]` and
  `SQLAlchemyProjectionResultReader[T]` expose only `one()`, `one_or_none()`, and `all()`.
- Application code uses concrete constructor-injected `SQLAlchemy...Repository` classes for entity
  persistence and `SQLAlchemy...Query` classes for read projections. Current database adapters have
  no duplicate Protocol layer, and persistence never imports application.
- Writes and reads remain separate. Repositories never commit, roll back, or implement Active Record.
- Structured Commands, Queries, domain values, pagination values, internal results, and read
  projections use immutable Pydantic v2 models. SQLAlchemy mappings and runtime resources do not.
- Typer exposes only `virtualMoney run`; production starts Gunicorn directly.
- Exception handlers pass exception objects to Logfire through `_exc_info`. Manual exception-type
  attributes, SQLSTATE tables, exception-string parsing, and redundant runtime type checks are forbidden.
- Public application errors use one logical error per file. SQLAlchemy Base, mixins, and one-model-per-file
  ORM mappings live under `persistence/database` and use relative package facades.

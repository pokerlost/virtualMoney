# virtualMoney

`virtualMoney` — backend-сервис платформы онлайн-покера и источник истины по внутренним
игровым средствам. Этот репозиторий содержит production-oriented каркас HTTP-приложения;
финансовая business logic будет добавляться отдельными этапами.

## Область ответственности

Сервис отвечает за будущую реализацию:

- assets и accounts;
- double-entry ledger и balances;
- holds и table escrow;
- buy-in, rebuy и cashout;
- rake и refunds;
- историю финансовых операций.

В сервис намеренно не входят blockchain, crypto wallets, private keys, on-chain deposits и
withdrawals, blockchain RPC, mainnet/testnet infrastructure. В текущем этапе также отсутствуют
финансовые entities, use cases и endpoints.

## Технологический стек

- Python 3.14.7;
- `uv` для Python, dependencies и virtual environment;
- FastAPI и Pydantic v2;
- SQLAlchemy 2.x async API, PostgreSQL и `asyncpg`;
- Alembic;
- Ruff Formatter/Ruff Linter, mypy и pre-commit.

Версия Python зафиксирована в `.python-version`, диапазон совместимости — в `pyproject.toml`,
а полный dependency graph — в `uv.lock`. Другие dependency managers не используются.

## Подготовка окружения

Установите `uv`, затем из корня репозитория выполните:

```bash
uv python install
uv sync --frozen
```

`uv` создаст `.venv` и использует Python из `.python-version`. Активировать окружение можно
явно:

```bash
source .venv/bin/activate
```

Активация не обязательна: все команды ниже запускаются через `uv run`.

Для локальной configuration при необходимости скопируйте пример:

```bash
cp .env.example .env
```

Значение `VIRTUAL_MONEY_DATABASE_URL` требуется для Alembic и будущих DB operations, но не для
запуска приложения и `GET /`. Файл `.env` исключён из Git; реальные credentials коммитить нельзя.

## Quality tools

Установите Git hooks один раз:

```bash
uv run pre-commit install
```

Запуск всех pre-commit hooks вручную:

```bash
uv run pre-commit run --all-files
```

Отдельные команды:

```bash
uv run ruff format .
uv run ruff format --check .
uv run ruff check .
uv run mypy
```

Ruff является единственным formatter. `mypy` сознательно не добавлен в pre-commit: отдельная
команда переиспользует lock-файл и project environment вместо хрупкого дублирования runtime
dependencies внутри hook environment.

Автотесты, fixtures, coverage и CI/CD намеренно не входят в этот этап и не настроены.

## Запуск HTTP-приложения

Application factory находится в `src/virtual_money/api/application.py`. Локальный запуск напрямую
через factory:

```bash
uv run uvicorn virtual_money.api.application:create_app --factory --host 127.0.0.1 --port 8000
```

Проверка корневого endpoint:

```bash
curl -i http://127.0.0.1:8000/
```

Ожидаемый JSON:

```json
{
  "ok": true,
  "result": null,
  "error": null,
  "errorMessage": null,
  "statusCode": 200
}
```

`GET /` подтверждает только доступность FastAPI HTTP application. Он не обращается к PostgreSQL и
не заменяет будущие health/readiness endpoints.

OpenAPI доступен по адресам:

- `http://127.0.0.1:8000/openapi.json`;
- `http://127.0.0.1:8000/docs`.

## API naming convention

- Python modules, identifiers, parameters, Pydantic fields и SQLAlchemy attributes используют
  `snake_case`.
- Публичный JSON всегда сериализуется в `camelCase`.
- Pydantic validation принимает canonical `snake_case`, публичный `camelCase` и дополнительный
  `PascalCase`.
- OpenAPI response schemas показывают публичные `camelCase` names.

Стратегия реализована централизованно в `common/naming.py` и применяется через `AppBaseModel`.
Aliases не задаются вручную в каждом endpoint.

## Pydantic infrastructure

Базовые responsibilities разделены:

1. `AppBaseModel` — строгая общая Pydantic v2 configuration и alias policy.
2. `ApiResponse[T]` — generic success/error envelope с validation внутренних invariants.
3. `OrmSchemaBase` — только schemas, создаваемые через `from_attributes=True`.
4. `EntitySchemaBase` — минимальная API schema сущности с typed UUID `id`.

Pydantic schemas не являются SQLAlchemy ORM models или domain entities.

## SQLAlchemy и Alembic

`persistence/base.py` содержит SQLAlchemy 2.x `DeclarativeBase`, стабильную metadata naming
convention и небольшой `UUIDPrimaryKeyMixin` с PostgreSQL server-side UUID. Timestamps и финансовые
columns пока не вводятся.

`persistence/session.py` предоставляет factories для `AsyncEngine` и
`async_sessionmaker[AsyncSession]`. Global engine/session и connection на import отсутствуют.

Alembic связан с `Base.metadata`. Для команды Alembic необходим корректный
`VIRTUAL_MONEY_DATABASE_URL` со схемой `postgresql+asyncpg`:

```bash
uv run alembic current
```

Начальная migration и фиктивные таблицы не создавались, поскольку ORM entities на этом этапе
отсутствуют.

## Структура

```text
alembic/                         # migration environment, пока без revisions
src/virtual_money/
    api/
        application.py          # FastAPI application factory
        errors/                 # centralized exception handlers
        routers/root.py         # GET /
        schemas/                # response и entity contracts
    common/
        models/                 # общие Pydantic bases
        naming.py               # input/output alias strategy
    configuration/settings.py   # validated pydantic-settings configuration
    persistence/
        base.py                 # SQLAlchemy Base, naming convention, UUID mixin
        session.py              # async engine/session factories
```

Новые directories следует создавать только под реально реализуемую ответственность. Подробные
архитектурные и documentation rules зафиксированы в `AGENTS.md`.

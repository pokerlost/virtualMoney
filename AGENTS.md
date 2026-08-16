# AGENTS.md

## Общие правила работы

Всегда отвечай пользователю на русском языке.

Все объяснения, комментарии и сообщения пиши на русском.
Код, имена переменных, названия библиотек, API, классов и технические термины оставляй на английском, если их обычно не переводят.

Перед изменением репозитория:

1. Прочитай корневой `AGENTS.md`.
2. Изучи существующую структуру проекта.
3. Следуй repository-specific правилам поверх общих правил.
4. Не выдумывай несуществующие пути, модули или архитектуру, если структура уже существует.
5. Сохраняй изменения строго в рамках поставленной задачи.

Не выполняй несвязанный рефакторинг.

Не изменяй публичный API без прямой необходимости.

Не выдумывай:
- результаты тестов;
- coverage;
- результаты benchmark;
- поддержку платформ;
- compatibility guarantees.

Не выполняй destructive Git-команды.

Не делай `git push`, если это явно не запросили.

Перед завершением задачи просмотри итоговый diff.

Сообщай:
- какие команды были выполнены;
- какие команды не удалось выполнить;
- какие зависимости или инструменты отсутствовали;
- какие допущения были сделаны;
- какие проблемы остались.

---

# Сервис

Этот репозиторий содержит backend-сервис платформы онлайн-покера.

Для `virtualMoney` сервис отвечает за внутренние игровые средства:

- assets;
- user accounts;
- double-entry ledger;
- balances;
- holds;
- buy-in;
- rebuy;
- cashout;
- table escrow;
- rake;
- refunds;
- историю финансовых операций.

Сервис является источником истины по внутренним игровым деньгам.

В сервисе запрещены:
- blockchain;
- crypto wallets;
- private keys;
- crypto addresses;
- on-chain deposits;
- on-chain withdrawals;
- blockchain RPC;
- mainnet/testnet logic.

Все денежные значения хранятся только в целых минимальных единицах.

`float` и `double` для денежных значений запрещены.

Financial records после проведения не изменяются и не удаляются.
Исправления выполняются через reversal/compensating operations.

Все важные изменяющие состояние операции должны быть идемпотентными.

---

# Основной стек

Используй:

- Python;
- FastAPI;
- Pydantic v2;
- SQLAlchemy 2.x;
- PostgreSQL;
- Alembic.

Дополнительные технологии добавляй только при конкретной необходимости.

Не добавляй Kafka, RabbitMQ, NATS, Redis или другой infrastructure dependency без обоснованной необходимости.

---

# Архитектурные слои

Код должен быть разделён по логическим слоям.

Предпочтительная структура:

```text
src/
    <service_package>/
        domain/
            entities/
            value_objects/
            enums/
            services/
            exceptions/

        application/
            commands/
            queries/
            use_cases/
            dto/
            ports/
            services/

        api/
            routers/
            schemas/
                requests/
                responses/
            dependencies/
            middleware/
            errors/
            security/
            application.py

        persistence/
            models/
            repositories/
            mappings/
            types/
            enums/
            unit_of_work/
            migrations_support/

        integrations/
            clients/
            adapters/
            schemas/

        workers/

        configuration/
            settings.py

        observability/
            logging.py
            metrics.py

        infrastructure/
```

Это концептуальная структура.

Не создавай пустые директории только ради соответствия схеме.

Если существующий проект уже имеет разумную структуру, адаптируйся к ней вместо полного переписывания.

---

# Направление зависимостей

Предпочтительное направление:

```text
api
 |
 v
application
 |
 v
domain

persistence -------> application/domain ports
integrations ------> application ports
configuration -----> composition root
observability -----> infrastructure/composition
```

`domain` не должен зависеть от внешних frameworks.

В `domain` запрещены imports из:

- FastAPI;
- Starlette;
- SQLAlchemy;
- Alembic;
- HTTP clients;
- PostgreSQL-specific libraries;
- environment/configuration libraries.

---

# FastAPI

## Общий стиль

Используй возможности FastAPI там, где они реально дают:

- parsing;
- validation;
- dependency injection;
- security;
- OpenAPI documentation;
- request metadata;
- response contracts.

Не выполняй ручной parsing HTTP-параметров, если FastAPI умеет сделать это корректно.

Предпочитай `typing.Annotated`.

Пример:

```python
user_id: Annotated[UUID, Path(...)]
limit: Annotated[int, Query(ge=1, le=100)]
idempotency_key: Annotated[str, Header(min_length=1, max_length=128)]
```

Используй по назначению:

- `Path`;
- `Query`;
- `Header`;
- `Cookie`;
- `Body`;
- `Form`;
- `File`;
- `Depends`;
- FastAPI security dependencies.

---

# Application factory

FastAPI-приложение должно собираться через application factory.

Предпочтительно:

```python
def create_app(settings: Settings | None = None) -> FastAPI:
    ...
    return app
```

Не выполняй всю конфигурацию приложения непосредственно на уровне module import.

Application factory отвечает за orchestration:

- создание `FastAPI`;
- metadata;
- routers;
- middleware;
- exception handlers;
- lifespan;
- OpenAPI configuration.

Сам `create_app()` должен оставаться небольшим.

Настройку выноси в отдельные функции:

```python
configure_middleware(app, settings)
configure_exception_handlers(app)
configure_routers(app)
```

---

# Routers

Используй `APIRouter`.

Разделяй routers по bounded API area или resource.

Не складывай все endpoints в один файл.

Route handler должен выполнять в основном:

1. HTTP parsing;
2. transport validation;
3. dependency resolution;
4. создание application command/query или передачу параметров use case;
5. вызов application layer;
6. mapping результата в API response.

Route handler не должен содержать:

- ledger calculations;
- SQL;
- transaction management;
- balance mutation logic;
- retry loops;
- integration logic;
- сложные state transitions.

---

# FastAPI metadata и OpenAPI

Для endpoint указывай при необходимости:

- `response_model`;
- `status_code`;
- `summary`;
- `description`;
- `responses`;
- `tags`;
- `operation_id`.

OpenAPI является частью публичного контракта сервиса.

Не используй неописанные `dict` как основной публичный API-контракт.

---

# Dependency Injection

Используй FastAPI `Depends` только на transport/composition boundary.

Предпочитай typed aliases:

```python
DatabaseSessionDep = Annotated[AsyncSession, Depends(get_db_session)]
CurrentPrincipalDep = Annotated[Principal, Depends(get_current_principal)]
```

DI подходит для:

- authentication principal;
- service identity;
- permissions/scopes;
- DB session;
- unit of work;
- application services;
- configuration;
- request metadata;
- integration adapters.

Не используй `Depends` внутри:

- domain;
- application use cases;
- persistence repositories;
- ORM models.

Application/domain код должен быть вызываем без FastAPI.

Запрещены service locator и скрытые global dependencies.

---

# Pydantic v2

## Базовая модель

Создай одну настроенную базовую Pydantic-модель проекта.

Например:

```python
from pydantic import BaseModel, ConfigDict


class AppBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
        from_attributes=True,
    )
```

Настройки адаптируй под реальную модель.

Не включай опции автоматически, если они мешают конкретному contract.

Используй Pydantic v2 API:

- `model_validate`;
- `model_dump`;
- `field_validator`;
- `model_validator`;
- `ConfigDict`;
- `computed_field`.

Не используй deprecated Pydantic v1 style.

---

# Разделение моделей

Не смешивай следующие типы моделей:

1. Domain entities/value objects.
2. Application DTO/commands/queries.
3. SQLAlchemy ORM models.
4. Pydantic API request models.
5. Pydantic API response models.
6. Integration schemas.

ORM model не является API schema.

API schema не является domain entity.

Не возвращай SQLAlchemy ORM objects напрямую наружу как публичный contract.

Для ORM сущностей создавай соответствующие Pydantic response schemas там, где сущность попадает в API.

Используй `from_attributes=True` для безопасного mapping ORM -> Pydantic только там, где это уместно.

Не заставляй API зависеть от persistence-specific полей.

---

# API schemas

Размещай API-схемы отдельно от ORM.

Например:

```text
api/
    schemas/
        requests/
            accounts.py
            ledger.py
            holds.py
        responses/
            accounts.py
            ledger.py
            holds.py
```

Допустимо объединять request/response schema в одном domain-oriented модуле, если файлов становится слишком много и разделение не улучшает читаемость.

Не создавай гигантский `schemas.py`.

---

# Общий API response envelope

Все обычные JSON endpoints должны использовать единый Generic response envelope, кроме осознанных protocol-specific исключений.

Пример:

```python
from typing import Generic, TypeVar

from pydantic import model_validator

T = TypeVar("T")


class ApiResponse(AppBaseModel, Generic[T]):
    ok: bool
    result: T | None = None
    error: str | None = None
    error_message: str | None = None
    status_code: int

    @model_validator(mode="after")
    def validate_response_state(self) -> "ApiResponse[T]":
        if self.ok:
            if self.error is not None or self.error_message is not None:
                raise ValueError("Successful response cannot contain error")
        else:
            if self.result is not None:
                raise ValueError("Error response cannot contain result")
            if not self.error or not self.error_message:
                raise ValueError("Error response must contain error information")
        return self
```

Successful response:

```json
{
  "ok": true,
  "result": {},
  "error": null,
  "error_message": null,
  "status_code": 200
}
```

Error response:

```json
{
  "ok": false,
  "result": null,
  "error": "HTTP_404_NOT_FOUND",
  "error_message": "Requested account was not found",
  "status_code": 404
}
```

`status_code` должен быть `int`.

Фактический HTTP status и `status_code` внутри response body должны совпадать.

Нельзя возвращать HTTP 200 при ошибке только потому, что error находится в JSON.

Не собирай response dictionaries вручную в каждом router.

Сделай централизованные success/error constructors или mappers, если это уменьшает дублирование.

---

# Error handling

Domain/application exceptions не должны зависеть от FastAPI.

Не используй `HTTPException` внутри domain/application/persistence.

Создавай typed exceptions для случаев вроде:

- entity not found;
- invalid state;
- conflict;
- insufficient funds;
- duplicate/idempotency conflict;
- permission violation;
- infrastructure unavailable.

На API boundary выполняй mapping application/domain errors -> HTTP responses.

Используй централизованные FastAPI exception handlers.

Unexpected errors:

- логируются;
- не раскрывают stack trace клиенту;
- не раскрывают внутренние SQL/credentials/secrets;
- возвращают безопасный generic error.

Запрещено:

```python
except Exception:
    pass
```

---

# HTTP status codes

Используй:

```python
from fastapi import status
```

Вместо magic numbers предпочитай:

```python
status.HTTP_200_OK
status.HTTP_201_CREATED
status.HTTP_204_NO_CONTENT
status.HTTP_400_BAD_REQUEST
status.HTTP_401_UNAUTHORIZED
status.HTTP_403_FORBIDDEN
status.HTTP_404_NOT_FOUND
status.HTTP_409_CONFLICT
status.HTTP_422_UNPROCESSABLE_ENTITY
status.HTTP_500_INTERNAL_SERVER_ERROR
status.HTTP_503_SERVICE_UNAVAILABLE
```

---

# SQLAlchemy 2.x

Используй современный SQLAlchemy 2.x declarative style.

Legacy querying и legacy model declaration запрещены.

---

# SQLAlchemy Declarative Base

Создай собственную declarative base.

Пример:

```python
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
```

Если необходимо определить общие ORM conventions, делай это централизованно.

Не смешивай declarative base с API/Pydantic base model.

---

# SQLAlchemy strict typing

ORM models должны быть полностью типизированы.

Используй:

- `Mapped[T]`;
- `mapped_column()`;
- `relationship()`;
- typed collections;
- Python enums;
- UUID/ULID wrapper types, если они действительно используются проектом.

Пример:

```python
from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column


class AccountModel(Base):
    __tablename__ = "accounts"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    balance_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
```

Не используй старый стиль:

```python
id = Column(...)
```

если проект не содержит legacy-код, который пока невозможно безопасно мигрировать.

---

# Собственные ORM типы

Persistence-specific типы должны находиться отдельно.

Предпочтительно:

```text
persistence/
    types/
        uuid.py
        money.py
        timestamps.py
```

или более компактная структура, если типов мало.

Создавай собственные SQLAlchemy types только если они обеспечивают реальную гарантию или единый mapping.

Примеры возможных задач:

- UUID/ULID representation;
- constrained monetary integer;
- domain enum mapping;
- JSON value object mapping.

Не создавай custom `TypeDecorator`, если стандартного SQLAlchemy/PostgreSQL type достаточно.

Если используется `TypeDecorator`:

- он должен быть typed;
- иметь `cache_ok = True`, когда это корректно;
- явно реализовывать conversion;
- не содержать business logic;
- не скрывать неочевидные side effects.

---

# Money types

Деньги в БД хранятся целым числом минимальных единиц.

Предпочтительно PostgreSQL `BIGINT`.

Использовать для money запрещено:

- `Float`;
- `REAL`;
- `DOUBLE PRECISION`;
- Python `float`.

Если создаётся Python alias/value object для monetary amount, он должен гарантировать integer semantics.

Например, допустимо иметь отдельный domain `Money`/`Amount` value object и persistence mapping для него.

---

# ORM enums

Closed state sets должны быть типизированы.

Python enum размещай в appropriate domain/persistence module в зависимости от ownership.

Не размазывай строковые состояния:

```python
status = "pending"
```

по всему проекту.

Используй enum.

При использовании PostgreSQL native ENUM заранее продумывай Alembic migration strategy.

Не изменяй enum values в production schema без migration.

Если native PostgreSQL enum усложняет evolution без ощутимой пользы, допустим String/VARCHAR storage + typed Python enum + DB constraint.

Выбор должен быть осознанным.

---

# ORM model structure

ORM models разделяй по bounded persistence area.

Например:

```text
persistence/
    models/
        account.py
        asset.py
        ledger.py
        hold.py
        table_escrow.py
        outbox.py
```

Не создавай один огромный `models.py`.

Если моделей мало, допустимо более компактное разделение.

ORM model содержит:

- DB columns;
- relationships;
- persistence constraints;
- indexes;
- simple persistence-oriented representation.

ORM model не должен содержать сложную business logic.

---

# ORM mixins

Допустимы небольшие typed mixins для действительно общих persistence concerns.

Например:

```text
persistence/
    models/
        mixins/
            timestamps.py
            identifiers.py
```

Не создавай mixin architecture ради пары повторяющихся строк.

Не добавляй generic repository/base service только ради устранения небольшого дублирования.

---

# Constraints и indexes

Критические invariants, которые можно дополнительно защитить на уровне БД, должны иметь DB constraints.

Используй при необходимости:

- `CheckConstraint`;
- `UniqueConstraint`;
- `ForeignKeyConstraint`;
- indexes;
- partial indexes PostgreSQL.

Но DB constraints являются дополнительной защитой, а не заменой domain/application validation.

Для idempotency identifiers, external operation identifiers и уникальных financial events создавай соответствующие unique constraints.

---

# Relationships

SQLAlchemy relationships должны быть typed.

Пример:

```python
entries: Mapped[list["LedgerEntryModel"]] = relationship(
    back_populates="transaction",
)
```

Не используй relationships как скрытый механизм выполнения бизнес-операций.

Избегай неявного mass loading.

Loader strategy выбирай осознанно.

Не полагайся на lazy loading в API serialization.

Не допускай N+1 queries в ожидаемых hot paths.

---

# ORM и Pydantic

Для API создавай отдельные Pydantic schemas.

Пример:

```python
class AccountResponse(AppBaseModel):
    id: UUID
    asset_code: str
    available_balance: int
    held_balance: int
```

ORM:

```python
class AccountModel(Base):
    ...
```

Domain:

```python
@dataclass(frozen=True)
class Account:
    ...
```

Это разные ответственности.

Нельзя использовать один универсальный класс одновременно как:

- SQLAlchemy entity;
- Pydantic request;
- Pydantic response;
- domain entity.

---

# Persistence mappings

Mapping между ORM и domain/application representations должен быть явным.

Для mapping выделяй modules, если mapping становится нетривиальным:

```text
persistence/
    mappings/
        account.py
        ledger.py
```

Примеры:

```python
def account_model_to_domain(model: AccountModel) -> Account:
    ...
```

```python
def ledger_entry_to_model(entity: LedgerEntry) -> LedgerEntryModel:
    ...
```

Не создавай сложный universal automapper.

Явный mapping предпочтительнее скрытой reflection magic.

---

# Repositories

Repository interfaces/ports размещай в `application/ports` или другом внутреннем слое.

SQLAlchemy implementations размещай в persistence layer.

Например:

```text
application/
    ports/
        account_repository.py

persistence/
    repositories/
        sqlalchemy_account_repository.py
```

Repository не должен:

- commit transaction самостоятельно без архитектурной причины;
- возвращать FastAPI response;
- выбрасывать `HTTPException`;
- содержать HTTP logic.

Repository отвечает за persistence operations.

Business decisions остаются в domain/application.

---

# Unit of Work

Для financial commands transaction boundary должен быть явным.

Предпочтительно использовать Unit of Work или эквивалентный application-level transaction boundary.

Пример концепции:

```python
async with uow:
    ...
    await uow.commit()
```

Не вызывай `commit()` внутри случайных low-level repository methods.

Одна логическая финансовая операция должна либо завершиться целиком, либо откатиться целиком.

Пример:

```text
BEGIN

idempotency check
domain validation
ledger transaction
ledger entries
hold/escrow state
outbox event

COMMIT
```

---

# Async SQLAlchemy

Если сервис использует async FastAPI stack, используй:

- `AsyncEngine`;
- `async_sessionmaker`;
- `AsyncSession`;
- SQLAlchemy async API.

Не смешивай sync и async DB access без явной причины.

Не делай blocking DB operations в async route handlers.

Session lifecycle должен быть deterministic.

---

# SQLAlchemy session

Не создавай global `AsyncSession`.

Не переиспользуй одну session между concurrent requests.

Обычно session должна жить в рамках request/application operation/UoW.

Session dependency может создаваться через FastAPI DI на API boundary.

Rollback errors нельзя молча игнорировать.

---

# Query style

Используй SQLAlchemy 2.x statements:

```python
stmt = select(AccountModel).where(AccountModel.id == account_id)
result = await session.execute(stmt)
```

Не используй legacy:

```python
session.query(...)
```

Используй осмысленные методы результата:

- `scalar_one()`;
- `scalar_one_or_none()`;
- `scalars()`;
- `one()`;
- `one_or_none()`.

Не используй `.first()` автоматически там, где uniqueness является invariant.

---

# Loading strategy

Выбирай loading strategy явно.

Используй по необходимости:

- `selectinload`;
- `joinedload`;
- explicit joins.

Не допускай неявной сериализации ORM graph с неожиданными дополнительными запросами.

Особенно не рассчитывай на lazy loading после закрытия session.

---

# Transactions и locking

Financial code должен учитывать concurrency.

Для операций, где возможна race condition, рассматривай:

- row-level locks;
- `SELECT ... FOR UPDATE`;
- unique constraints;
- optimistic versioning;
- atomic SQL updates.

Не используй locking автоматически везде.

Выбирай механизм согласно конкретному invariant.

Нельзя проверять баланс одним запросом, затем без защиты изменять его другим запросом, если параллельная операция может нарушить invariant.

---

# Ledger

Ledger должен быть immutable double-entry.

Каждая financial transaction должна иметь минимум две противоположные entries.

Сумма entries по одной asset должна быть равна нулю.

Ledger transaction и entries должны сохраняться атомарно.

Проведённая ledger transaction не редактируется.

Для correction создаётся reversal/compensating transaction.

Не изменяй authoritative balance скрытым SQL `UPDATE`, обходящим ledger.

Если balances materialized/cached для производительности, ledger остаётся authoritative financial history, а обновление materialized balance выполняется в той же transaction boundary.

---

# Holds

Holds должны моделироваться отдельной сущностью/состоянием.

Не реализуй hold простым уменьшением balance без истории.

Минимально продумай состояния вроде:

- active;
- released;
- captured;
- expired/cancelled, если это требуется business rules.

Повторная release/capture не должна повторно изменять средства.

---

# Table escrow

Table escrow должен быть отдельным account/ledger concept.

Buy-in переводит средства из пользовательского доступного account в table escrow.

Cashout переводит средства из table escrow обратно на user account.

Rake должен отражаться отдельной ledger operation и системным rake account.

Не храни table money только в Poker Server memory.

---

# Idempotency

Все важные state-changing operations получают стабильный identifier:

- `operation_id`;
- `idempotency_key`;
- `command_id`.

При сетевом retry используется тот же identifier.

Повтор не должен повторно:

- списывать средства;
- зачислять средства;
- создавать hold;
- захватывать hold;
- делать buy-in;
- делать rebuy;
- делать cashout;
- начислять rake;
- делать refund.

Idempotency record и financial mutation должны находиться в согласованной transaction boundary.

---

# Transactional outbox

Если операция создаёт исходящее событие, изменение состояния и outbox record должны сохраняться атомарно:

```text
BEGIN

state mutation
ledger mutation
outbox record

COMMIT
```

Для первой версии PostgreSQL outbox допустим и предпочтителен перед добавлением message broker без необходимости.

---

# Alembic

Все schema changes выполняй через Alembic migrations.

Не изменяй production schema вручную.

Migration должна:

- быть детерминированной;
- иметь понятные upgrade/downgrade, если downgrade безопасен;
- создавать indexes/constraints явно;
- корректно обрабатывать PostgreSQL-specific types;
- не уничтожать данные без прямого требования.

Не полагайся слепо на Alembic autogenerate.

После autogenerate всегда проверяй migration вручную.

При изменении enum/type учитывай отдельный migration lifecycle.

---

# Naming conventions

Используй единообразные DB names.

Предпочтительно настроить SQLAlchemy metadata naming convention для:

- primary keys;
- foreign keys;
- unique constraints;
- check constraints;
- indexes.

Например:

```python
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
```

Конкретную convention адаптируй под проект.

Это помогает Alembic создавать стабильные migrations.

---

# Configuration

Configuration должна быть централизована и validated.

Предпочтительно использовать `pydantic-settings`.

Не читай `os.environ` в arbitrary modules.

Settings загружаются в configuration/composition boundary.

Invalid required configuration должна приводить к fail-fast startup.

Secrets запрещено:

- хранить в Git;
- логировать;
- возвращать через API.

---

# Lifespan

Используй FastAPI lifespan вместо deprecated startup/shutdown events.

Lifespan подходит для lifecycle:

- DB engine;
- HTTP pools;
- infrastructure clients.

Не запускай unmanaged endless loops внутри lifespan.

Persistent background workers должны иметь отдельный явный lifecycle.

---

# Middleware

Middleware предназначен для cross-cutting transport concerns:

- request ID;
- correlation ID;
- logging context;
- timing/metrics;
- security headers.

Middleware не должен содержать:

- authorization business rules;
- ledger operations;
- balance mutation;
- DB-heavy logic без необходимости.

---

# Observability

Production-код должен поддерживать:

- structured JSON logging;
- `request_id`;
- `correlation_id`;
- `operation_id`;
- health endpoint;
- readiness endpoint;
- metrics-ready instrumentation.

Не логируй secrets.

Financial operation должна быть traceable по `operation_id`.

---

# Security

Следуй least privilege.

Сервис должен самостоятельно валидировать входящие данные и caller permissions.

Не доверяй client-provided значениям для:

- authoritative balances;
- rake calculations;
- account ownership;
- table balances;
- calculated fees.

Admin/internal operations должны иметь отдельные scopes/permissions.

Sensitive operations должны быть пригодны для rate limiting.

---

# Кодстайл

Код должен быть production-grade.

Предпочитай:

- explicit typing;
- ясные имена;
- небольшие focused modules;
- enums для закрытых состояний;
- immutable value objects, где это полезно;
- explicit dependencies;
- explicit transaction boundaries.

Избегай:

- `Any` без необходимости;
- magic strings;
- magic numbers;
- circular imports;
- import-time side effects;
- global mutable state;
- giant `utils.py`;
- giant `models.py`;
- giant `schemas.py`;
- giant `services.py`;
- скрытых DB writes;
- чрезмерного inheritance;
- generic abstractions без реальной пользы.

Не создавай абстракцию только ради "clean architecture".

---

# Запрещённые production-паттерны

Не допускаются:

- production state только в memory;
- global mutable singletons;
- `except Exception: pass`;
- silent error swallowing;
- hardcoded secrets;
- unvalidated env variables;
- скрытое изменение balance;
- прямое изменение таблиц другого сервиса;
- TODO вместо обязательного функционала завершённого этапа;
- фиктивная business logic;
- неограниченные retry;
- endless unmanaged background loops.

---

# Автотесты и CI/CD

Автотесты и CI/CD в рамках задач этого репозитория не реализовывать, если пользователь прямо не запросил обратное.

Запрещено добавлять или изменять:

- unit tests;
- integration tests;
- end-to-end tests;
- fixtures;
- coverage tooling;
- GitHub Actions;
- GitLab CI;
- Jenkins;
- CI pipeline;
- automatic deployment;
- CI runners.

Другой разработчик отвечает за tests и CI/CD.

Архитектура при этом должна оставаться testable:

- dependencies передаются явно;
- infrastructure находится за adapters/ports;
- system time можно подменить там, где он влияет на business behavior;
- business logic deterministic, где это возможно;
- application/domain код не требует FastAPI для запуска.

---

# Ручная проверка

Для проверки задач разрешены:

- запуск приложения;
- formatter;
- linter;
- type checker, если уже настроен;
- сборка;
- Alembic migration;
- `curl`;
- smoke-check;
- проверка записей в локальной PostgreSQL;
- существующий Docker Compose.

Не добавляй tests в acceptance criteria.

---

# Работа с изменениями

При выполнении конкретной задачи:

1. Сначала изучи текущую реализацию.
2. Определи минимально необходимую область изменений.
3. Не переписывай несвязанные модули.
4. Не меняй public contracts без необходимости.
5. Не добавляй новые dependencies без обоснования.
6. Не добавляй tests/CI.
7. Не оставляй основной функционал в TODO.
8. После реализации просмотри diff.
9. Выполни доступные ручные проверки.
10. В финальном отчёте укажи:
   - что сделано;
   - список изменённых файлов;
   - migrations;
   - новые/изменённые API contracts;
   - выполненные команды;
   - невыполненные команды и причины;
   - допущения;
   - риски;
   - незавершённые проблемы.

Если требования задачи конфликтуют с этим `AGENTS.md`, явно сообщи о конфликте и следуй более конкретному/новому прямому требованию пользователя.

---

# Обязательные conventions каркаса virtualMoney

- Python modules, variables, functions, parameters, Pydantic fields и SQLAlchemy attributes всегда
  используют `snake_case`.
- Публичная JSON serialization использует `camelCase`. Входная Pydantic validation принимает
  canonical `snake_case`, публичный `camelCase` и `PascalCase` через централизованную alias policy.
- Все API contracts наследуются от общей Pydantic v2 base model. ORM-facing Pydantic schemas,
  SQLAlchemy models и domain models остаются отдельными типами и не смешивают inheritance.
- SQLAlchemy mappings используют только typed стиль 2.x: `Mapped[T]`, `mapped_column`, typed
  `relationship` и SQLAlchemy 2.x statements. Legacy `Column` declarations и `session.query()`
  запрещены.
- Каждый публичный endpoint обязан явно задавать `summary`, `description`, `operation_id`,
  `response_model` и `status_code`; дополнительные исходы документируются через `responses`.
- Каждый публичный `Path`, `Query`, `Header`, `Cookie`, `Body`, `Form` и `File` parameter обязан
  иметь понятные `title`/`description`, ограничения и формат, когда FastAPI это поддерживает.
- Public/reusable functions и classes, dependency providers, application factory, non-obvious
  infrastructure и сложные invariants документируются содержательными docstrings.
- Tests, fixtures, coverage и CI/CD нельзя добавлять или изменять без прямого запроса пользователя.

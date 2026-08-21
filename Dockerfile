FROM ghcr.io/astral-sh/uv:0.8.15 AS uv

FROM python:3.12-slim-bookworm AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv
WORKDIR /build

COPY --from=uv /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev --no-install-project

FROM python:3.12-slim-bookworm AS runtime

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/service/app \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/opt/venv
WORKDIR /service

RUN groupadd --gid 10001 app \
    && useradd --uid 10001 --gid app --no-create-home --shell /usr/sbin/nologin app

COPY --from=builder /opt/venv /opt/venv
COPY app ./app
COPY alembic.ini ./alembic.ini
COPY alembic ./alembic

USER 10001:10001
EXPOSE 8000
CMD ["gunicorn", "api.application:create_app()", "--worker-class", "uvicorn_worker.UvicornWorker", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "30", "--graceful-timeout", "30", "--keep-alive", "5"]

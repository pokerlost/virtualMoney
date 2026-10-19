# syntax=docker/dockerfile:1.27.1@sha256:4edf897a3ffa55b89f906fc8cc78afdb3f1834cc9c7083565e611a8a7d5fe99e
ARG PYTHON_IMAGE=python:3.14.7-slim-bookworm@sha256:82bc3c539b8813ada9d68c63b40158fa002f7f33de9bf3312a3dfdc0620dff56

FROM ghcr.io/astral-sh/uv:0.12.15@sha256:62f8c047d0a0e9ece6b53fc63df902585a67a47a7f318ddec4a37db586edc8e3 AS uv

FROM ${PYTHON_IMAGE} AS base
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app

FROM base AS dependencies
COPY --from=uv /uv /usr/local/bin/uv
ENV UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never
COPY pyproject.toml uv.lock README.md .gitignore ./
RUN apt-get update \
    && apt-get install -y --no-install-recommends git make ca-certificates \
    && rm -rf /var/lib/apt/lists/*
COPY --chmod=0755 docker/sdk_askpass.sh /usr/local/bin/sdk_askpass
RUN --mount=type=cache,id=uv-runtime,target=/root/.cache/uv,sharing=locked \
    --mount=type=secret,id=sdk_token,required=true \
    GIT_CONFIG_COUNT=1 \
    GIT_CONFIG_KEY_0=url.https://github.com/pokerlost/pypokerlost.git.insteadOf \
    GIT_CONFIG_VALUE_0=ssh://git@github.com/pokerlost/pypokerlost.git \
    GIT_ASKPASS=/usr/local/bin/sdk_askpass GIT_TERMINAL_PROMPT=0 \
    UV_NO_GITHUB_FAST_PATH=1 \
    uv sync --locked --no-dev --no-install-project

FROM dependencies AS wheel-builder
RUN --mount=type=cache,id=uv-development,target=/root/.cache/uv,sharing=locked \
    --mount=type=secret,id=sdk_token,required=true \
    GIT_CONFIG_COUNT=1 \
    GIT_CONFIG_KEY_0=url.https://github.com/pokerlost/pypokerlost.git.insteadOf \
    GIT_CONFIG_VALUE_0=ssh://git@github.com/pokerlost/pypokerlost.git \
    GIT_ASKPASS=/usr/local/bin/sdk_askpass GIT_TERMINAL_PROMPT=0 \
    UV_NO_GITHUB_FAST_PATH=1 \
    uv sync --locked --all-groups --no-install-project
COPY src ./src
RUN --mount=type=cache,id=uv-build,target=/root/.cache/uv,sharing=locked \
    uv build --no-build-isolation --wheel --sdist --out-dir /dist

FROM wheel-builder AS quality
RUN uv pip install --python /app/.venv/bin/python --no-deps /dist/*.whl
COPY --chmod=u=rwX,go=rX . ./
ENV CONTAINERIZED=1
CMD ["make", "check"]

FROM scratch AS artifacts
COPY --from=wheel-builder /dist/ /

FROM dependencies AS installed
COPY --from=wheel-builder /dist/*.whl /wheels/
RUN uv pip install --python /app/.venv/bin/python --no-deps /wheels/*.whl

FROM wheel-builder AS test
RUN uv pip install --python /app/.venv/bin/python --no-deps /dist/*.whl
WORKDIR /checks
COPY --exclude=src --exclude=src/** --chmod=u=rwX,go=rX . ./
ENV COVERAGE_FILE=/checks/coverage/.coverage TEST_INSTALLED_WHEEL=1
USER 65532:65532
CMD ["python", "-m", "pytest", "--cov", "--cov-report=term-missing", "--cov-report=json", "--cov-report=xml", "-p", "no:cacheprovider"]

FROM base AS runtime
COPY --from=installed /app/.venv /app/.venv
USER 65532:65532
EXPOSE 8000
STOPSIGNAL SIGTERM
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.build_opener(urllib.request.ProxyHandler({})).open('http://127.0.0.1:8000/health/live', timeout=2).close()"]
CMD ["python", "-m", "uvicorn", "virtualmoney.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000", "--no-server-header", "--timeout-graceful-shutdown", "10"]

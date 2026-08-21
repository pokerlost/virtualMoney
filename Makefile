.DEFAULT_GOAL := help

.PHONY: help install run serve format lint typecheck pre-commit
.PHONY: db-upgrade db-downgrade db-revision

help:
	@printf '%-15s %s\n' \
		'install' 'Resolve and sync all dependency groups' \
		'run' 'Run the FastAPI application locally' \
		'serve' 'Run the production Gunicorn server' \
		'format' 'Format Python source code' \
		'lint' 'Run Ruff lint checks' \
		'typecheck' 'Run mypy static typing' \
		'pre-commit' 'Run configured pre-commit hooks' \
		'db-upgrade' 'Apply all Alembic migrations' \
		'db-downgrade' 'Roll back one Alembic migration' \
		'db-revision' 'Create migration: make db-revision name="description"'

install:
	uv sync --all-groups

run:
	PYTHONPATH=app uv run python -m cli run

serve:
	PYTHONPATH=app uv run gunicorn "api.application:create_app()" --worker-class uvicorn_worker.UvicornWorker --bind 0.0.0.0:8000 --workers 2

format:
	uv run ruff format app alembic

lint:
	uv run ruff check app alembic

typecheck:
	uv run mypy

pre-commit:
	uv run pre-commit run --all-files

db-upgrade:
	PYTHONPATH=app uv run alembic upgrade head

db-downgrade:
	PYTHONPATH=app uv run alembic downgrade -1

db-revision:
	@test -n "$(name)" || { echo 'Usage: make db-revision name="description"'; exit 2; }
	PYTHONPATH=app uv run alembic revision --autogenerate -m "$(name)"

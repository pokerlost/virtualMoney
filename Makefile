ifneq ($(CONTAINERIZED),1)
QUALITY_IMAGE := virtualmoney:quality
# Generated check owns its complete graph; opt into extras only when defined.
QUALITY_EXTRA_TARGETS :=
BUILD_DOCKERFILE := Dockerfile.quality
QUALITY_RUN_ARGS += --env TEST_DATABASE_URL --env DATABASE_URL

.PHONY: run
run:
	$(MAKE) CONTAINERIZED=1 run
QUALITY_EXTRA_TARGETS := chart-check
CI_LOCAL_TARGETS := check coverage build verify chart release-check
VERSION_COMMAND = $(QUALITY_RUN) python -m docker.chart_release version
RELEASE_CHECK_COMMAND = $(QUALITY_RUN) python -m docker.chart_release release-check
.PHONY: chart
chart: quality-image
	$(QUALITY_RUN) make chart

QUALITY_DOCKERFILE := Dockerfile
RUNTIME_IMAGE := virtualmoney:candidate
BUILD_DOCKERFILE := Dockerfile
VERIFY_COMMAND = $(MAKE) CONTAINERIZED=1 test-image && $(QUALITY_RUN) python docker/coverage_report.py coverage/installed/coverage.json --after coverage/installed/.started --output coverage/installed/summary.md
verify: quality-image
.PHONY: chart deploy-local undeploy-local
deploy-local undeploy-local:
	$(MAKE) CONTAINERIZED=1 $@


SOURCE_REQUIRE_LOCK ?= true
.PHONY: source
source:
	$(DOCKER) buildx build --file Dockerfile.source --build-arg REQUIRE_LOCK=$(SOURCE_REQUIRE_LOCK) --target source --load --tag virtualmoney:source $(QUALITY_BUILD_ARGS) .
	$(DOCKER) run --init --rm --read-only --network none --tmpfs /tmp:rw,mode=1777 --user "$$(id -u):$$(id -g)" virtualmoney:source

include docker/quality-python.mk
else
.DEFAULT_GOAL := help
UV ?= uv

.PHONY: help install format lint typecheck test test-unit check build

help: ## Show the supported development commands.
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z0-9_-]+:.*## / {printf "  %-18s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install the locked development environment.
	$(UV) sync --locked

format: ## Format owned Python sources.
	$(UV) run --locked ruff check --fix .
	$(UV) run --locked ruff format .

lint: ## Check formatting and lint without modifying files.
	$(UV) run --locked ruff check .
	$(UV) run --locked ruff format --check .

typecheck: ## Check strict Python types.
	$(UV) run --locked mypy

test-unit: ## Run isolated tests and complete Python coverage.
	$(UV) run --locked pytest --junitxml=coverage/junit.xml --cov --cov-report=term-missing --cov-report=json --cov-report=xml

test: test-unit ## Run every test required by this project's capabilities.


check: lint typecheck test ## Run the mandatory non-mutating checks.
	$(UV) lock --check

build: ## Export the wheel and sdist from the canonical container build.
	$(UV) build --no-build-isolation --wheel --sdist

.PHONY: image
image: ## Build and load the immutable runtime candidate locally.
	@mkdir -p dist
	docker buildx build $(DOCKER_BUILD_ARGS) $(LOCAL_BUILD_NETWORK) --target runtime --load --tag virtualmoney:candidate --metadata-file dist/image-build.json .

.PHONY: run

HTTP_HOST ?= 127.0.0.1
HTTP_PORT ?= 8000
UVICORN_FLAGS ?=

run: ## Run the application on loopback without rebuilding.
	$(UV) run --locked uvicorn virtualmoney.app:create_app --factory --host "$(HTTP_HOST)" --port "$(HTTP_PORT)" --no-server-header --no-access-log --log-config app_logging.json --workers 1 $(UVICORN_FLAGS)

.PHONY: test-image
test-image: ## Run installed-wheel tests in a disposable container and, when enabled, PostgreSQL.
	@mkdir -p coverage/installed
	docker buildx build $(DOCKER_BUILD_ARGS) $(LOCAL_BUILD_NETWORK) --target test --load --tag virtualmoney:test .
	@touch coverage/installed/.started
	docker run --rm --read-only --network none --tmpfs /tmp:rw,noexec,nosuid,size=64m --user "$$(id -u):$$(id -g)" --mount type=bind,source="$$(pwd)/coverage/installed",target=/checks/coverage virtualmoney:test

HELM ?= helm
KIND ?= kind
KUBECTL ?= kubectl
KUBECONFIG_LOCAL ?= $(CURDIR)/.local/kubeconfig
KIND_IMAGE := kindest/node:v1.37.0@sha256:a1ed56cfb0e7b93589bdf97c8cd566405a265939e3620fc4f5de89adff580ae5

.PHONY: chart chart-check
check: chart-check
chart: ## Package the managed shared chart as a deployable artifact.
	$(HELM) package deploy/chart --destination dist/charts --app-version "$$($(UV) run --locked python -m docker.chart_release app-version)"
	$(UV) run --locked python -m docker.chart_release capture

chart-check: ## Check chart templates and schema with explicit validation-only values.
	$(HELM) lint deploy/chart --strict --set image.repository=validation.invalid/application --set image.digest=sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa

.PHONY: deploy-local undeploy-local
deploy-local: image ## Create a disposable Kind contour; no external kubeconfig is used.
	@mkdir -p .local
	$(KIND) create cluster --name virtualmoney-local --image $(KIND_IMAGE) --kubeconfig $(KUBECONFIG_LOCAL) --wait 180s
	$(KIND) load docker-image virtualmoney:candidate --name virtualmoney-local
	$(KUBECTL) --kubeconfig $(KUBECONFIG_LOCAL) --context kind-virtualmoney-local create namespace foundation
	$(HELM) upgrade --install virtualmoney deploy/chart --kubeconfig $(KUBECONFIG_LOCAL) --kube-context kind-virtualmoney-local --namespace foundation --wait --timeout 120s --rollback-on-failure --values deploy/values.yaml --set image.repository=virtualmoney --set image.tag=candidate --set localDevelopment=true

undeploy-local: ## Delete only this application's disposable Kind cluster.
	$(KIND) delete cluster --name virtualmoney-local


# Project-owned commands survive Copier updates without copying shared recipes.
-include Makefile.local

endif

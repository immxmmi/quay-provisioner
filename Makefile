# ============================================================================
#  PipelineExecutionPlatform - Makefile
# ============================================================================

# --- Configuration -----------------------------------------------------------
PYTHON     ?= python
SRC_DIR    := src
PY_VERSION ?= 3.12

# --- Container Configuration -------------------------------------------------
REGISTRY   ?= quay.io
NAMESPACE  ?= your-repo
IMAGE_NAME ?= quay-provisioner
VERSION    ?= 0.0.2
TAG        ?= $(VERSION)

IMAGE_REF     := $(REGISTRY)/$(NAMESPACE)/$(IMAGE_NAME):$(TAG)
IMAGE_LOCAL   := $(IMAGE_NAME):$(TAG)
BASE_IMAGE    := quay.io/lib/python:$(PY_VERSION)
COMPOSE_FILE  := environment/quay/docker-compose.yaml

# Git-based version (optional, use with: make build TAG=$(shell git describe --tags --always))
GIT_COMMIT    := $(shell git rev-parse --short HEAD 2>/dev/null || echo "unknown")

# --- Helm Configuration ------------------------------------------------------
HELM_CHART     := helm
HELM_RELEASE   ?= quay-provisioner
HELM_NAMESPACE ?= quay-system
HELM_VALUES    ?= helm/values.yaml

# --- .PHONY Declarations -----------------------------------------------------
.PHONY: help run run-debug test lint lint-fix check clean \
        quay-up quay-down quay-logs quay-status \
        build build-offline run-container run-offline \
        export push login push-buildah \
        wheelhouse wheelhouse-clean check-python info \
        helm-lint helm-template helm-package helm-install helm-uninstall \
        helm-upgrade helm-dry-run helm-status helm-clean

.DEFAULT_GOAL := help

# ============================================================================
#  Help
# ============================================================================

help:
	@echo ""
	@echo "  \033[1;36mPipelineExecutionPlatform\033[0m"
	@echo "  ─────────────────────────────────────────────────────"
	@echo ""
	@echo "  \033[1mPython Development:\033[0m"
	@echo "    run              Run the pipeline"
	@echo "    run-debug        Run with debug output and CURL commands"
	@echo "    test             Run syntax checks and unit tests"
	@echo "    lint             Run linting with ruff"
	@echo "    lint-fix         Auto-fix linting issues"
	@echo "    check            Run all checks (lint + test)"
	@echo "    clean            Remove cache files"
	@echo ""
	@echo "  \033[1mQuay Environment:\033[0m"
	@echo "    quay-up          Start local Quay test environment"
	@echo "    quay-down        Stop Quay test environment"
	@echo ""
	@echo "  \033[1mDocker:\033[0m"
	@echo "    build            Build Docker image (TAG=x.x.x)"
	@echo "    build-offline    Build offline Docker image"
	@echo "    run-container    Run Docker container"
	@echo "    run-offline      Run offline container"
	@echo "    export           Export image to tar file"
	@echo "    push             Push image to registry"
	@echo "    login            Login to container registry"
	@echo ""
	@echo "  \033[1mVariables:\033[0m"
	@echo "    TAG=1.0.0        Set image tag/version"
	@echo "    REGISTRY=...     Set container registry"
	@echo "    NAMESPACE=...    Set registry namespace"
	@echo ""
	@echo "  \033[1mHelm:\033[0m"
	@echo "    helm-lint        Lint the Helm chart"
	@echo "    helm-template    Render templates locally"
	@echo "    helm-dry-run     Test install (no actual deploy)"
	@echo "    helm-install     Install chart to Kubernetes"
	@echo "    helm-upgrade     Upgrade existing release"
	@echo "    helm-uninstall   Remove release from cluster"
	@echo "    helm-status      Show release status"
	@echo "    helm-package     Package chart into .tgz"
	@echo "    helm-clean       Remove packaged charts"
	@echo ""
	@echo "  \033[1mUtilities:\033[0m"
	@echo "    wheelhouse       Create Python wheels for offline builds"
	@echo "    wheelhouse-clean Clean wheelhouse directory"
	@echo "    check-python     Check Python version in base image"
	@echo "    info             Show current configuration"
	@echo ""
	@echo "  \033[1mHelm Variables:\033[0m"
	@echo "    HELM_RELEASE=... Release name (default: quay-provisioner)"
	@echo "    HELM_NAMESPACE=. Namespace (default: quay-system)"
	@echo "    HELM_VALUES=...  Custom values file"
	@echo ""
	@echo "  \033[2mUsage: make <target>\033[0m"
	@echo ""

# ============================================================================
#  Python Development
# ============================================================================

run:
	@cd $(SRC_DIR) && $(PYTHON) main.py

run-debug:
	@cd $(SRC_DIR) && DEBUG_ENABLED=true SHOW_CURL=true $(PYTHON) main.py

test:
	@echo "\033[1;34m=== Syntax Check ===\033[0m"
	@cd $(SRC_DIR) && find . -name "*.py" -not -path "./__pycache__/*" | xargs $(PYTHON) -m py_compile
	@echo "\033[32m✓ Syntax check passed\033[0m"
	@echo ""
	@echo "\033[1;34m=== Import Tests ===\033[0m"
	@cd $(SRC_DIR) && $(PYTHON) -c "from exceptions import PipelineError, QuayApiError, ValidationError; print('\033[32m✓\033[0m exceptions')"
	@cd $(SRC_DIR) && $(PYTHON) -c "from actions.base_action import BaseAction; print('\033[32m✓\033[0m base_action')"
	@cd $(SRC_DIR) && $(PYTHON) -c "from actions.create_organization import CreateOrganizationAction; print('\033[32m✓\033[0m actions')"
	@cd $(SRC_DIR) && $(PYTHON) -c "from config.loader import Config; print('\033[32m✓\033[0m config')"
	@cd $(SRC_DIR) && $(PYTHON) -c "from gateway.client import ApiClient; print('\033[32m✓\033[0m gateway')"
	@cd $(SRC_DIR) && $(PYTHON) -c "from engine.pipeline_engine import PipelineEngine; print('\033[32m✓\033[0m engine')"
	@echo ""
	@echo "\033[1;34m=== Unit Tests ===\033[0m"
	@cd $(SRC_DIR) && $(PYTHON) -c "from config.loader import Config; c1 = Config(); c2 = Config(); assert c1 is c2, 'Singleton failed'; print('\033[32m✓\033[0m Config singleton'); Config.reset()"
	@cd $(SRC_DIR) && $(PYTHON) -c "from gateway.client import ApiClient; client = ApiClient(); masked = client._mask_sensitive_headers({'Authorization': 'secret', 'Content-Type': 'json'}); assert masked['Authorization'] == '***REDACTED***'; print('\033[32m✓\033[0m Header masking')"
	@cd $(SRC_DIR) && $(PYTHON) -c "from gateway.quay_gateway import _safe_path; assert _safe_path('test/path') == 'test%2Fpath'; print('\033[32m✓\033[0m URL encoding')"
	@echo ""
	@echo "\033[1;32m=== All tests passed! ===\033[0m"

lint:
	@command -v ruff >/dev/null 2>&1 && ruff check $(SRC_DIR) || echo "\033[33mruff not installed. Run: pip install ruff\033[0m"

lint-fix:
	@command -v ruff >/dev/null 2>&1 && ruff check $(SRC_DIR) --fix || echo "\033[33mruff not installed. Run: pip install ruff\033[0m"

check: lint test

clean:
	@echo "Cleaning cache files..."
	@find $(SRC_DIR) -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find $(SRC_DIR) -type f -name "*.pyc" -delete 2>/dev/null || true
	@find $(SRC_DIR) -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "\033[32m✓ Cleaned\033[0m"

# ============================================================================
#  Quay Environment
# ============================================================================

quay-up:
	@echo "Starting Quay environment..."
	@docker compose -f $(COMPOSE_FILE) up -d
	@echo "\033[32m✓ Quay environment started\033[0m"
	@echo "  Access: http://127.0.0.1:9080"

quay-down:
	@echo "Stopping Quay environment..."
	@docker compose -f $(COMPOSE_FILE) down
	@echo "\033[32m✓ Quay environment stopped\033[0m"

quay-logs:
	@docker compose -f $(COMPOSE_FILE) logs -f

quay-status:
	@docker compose -f $(COMPOSE_FILE) ps

# ============================================================================
#  Docker Build & Run
# ============================================================================

build:
	@echo "Building Docker image: $(IMAGE_LOCAL)..."
	@docker build \
		--build-arg VERSION=$(TAG) \
		--build-arg GIT_COMMIT=$(GIT_COMMIT) \
		-t $(IMAGE_LOCAL) \
		-t $(IMAGE_NAME):latest \
		.
	@echo "\033[32m✓ Image built: $(IMAGE_LOCAL)\033[0m"

build-offline:
	@echo "Building offline Docker image: $(IMAGE_NAME)-offline:$(TAG)..."
	@docker build \
		--build-arg VERSION=$(TAG) \
		-f Dockerfile_offline \
		-t $(IMAGE_NAME)-offline:$(TAG) \
		-t $(IMAGE_NAME)-offline:latest \
		.
	@echo "\033[32m✓ Offline image built: $(IMAGE_NAME)-offline:$(TAG)\033[0m"

run-container:
	@docker run --rm -it \
		--network host \
		-v $(PWD)/src/pipelines:/app/pipelines \
		$(IMAGE_NAME)

run-offline:
	@docker run --rm -it \
		--network host \
		-v $(PWD)/src/pipelines:/app/pipelines \
		$(IMAGE_NAME)-offline

export: build
	@echo "Exporting Docker image..."
	@docker save $(IMAGE_NAME) -o $(IMAGE_NAME).tar
	@echo "\033[32m✓ Image exported to $(IMAGE_NAME).tar\033[0m"

# ============================================================================
#  Registry Operations
# ============================================================================

login:
	@echo "Logging in to $(REGISTRY)..."
	@docker login $(REGISTRY)

push: build
	@echo "Pushing image to $(IMAGE_REF)..."
	@docker tag $(IMAGE_NAME) $(IMAGE_REF)
	@docker push $(IMAGE_REF)
	@echo "\033[32m✓ Image pushed: $(IMAGE_REF)\033[0m"

# --- Buildah alternative (use CONTAINER_ENGINE=buildah) ---
push-buildah: login
	@echo "Building and pushing with buildah..."
	@buildah bud -f Dockerfile -t $(IMAGE_REF) .
	@buildah push $(IMAGE_REF)
	@echo "\033[32m✓ Image pushed: $(IMAGE_REF)\033[0m"

# ============================================================================
#  Utilities
# ============================================================================

wheelhouse:
	@mkdir -p wheels
	@docker run --rm \
		-v "$(PWD)/requirements.txt:/requirements.txt" \
		-v "$(PWD)/wheels:/wheels" \
		$(BASE_IMAGE) \
		sh -c "pip install --upgrade pip && pip download --only-binary=:all: -r /requirements.txt -d /wheels"
	@echo "\033[32m✓ Wheelhouse created in ./wheels\033[0m"

wheelhouse-clean:
	@rm -rf wheels && mkdir wheels
	@echo "\033[32m✓ Wheelhouse cleaned\033[0m"

check-python:
	@docker run --rm $(BASE_IMAGE) python --version

info:
	@echo ""
	@echo "  \033[1mConfiguration:\033[0m"
	@echo "  ─────────────────────────────────────"
	@echo "  Python:       $(PYTHON)"
	@echo "  Source:       $(SRC_DIR)"
	@echo ""
	@echo "  \033[1mContainer:\033[0m"
	@echo "  ─────────────────────────────────────"
	@echo "  Registry:     $(REGISTRY)"
	@echo "  Namespace:    $(NAMESPACE)"
	@echo "  Image:        $(IMAGE_NAME)"
	@echo "  Tag:          $(TAG)"
	@echo "  Git Commit:   $(GIT_COMMIT)"
	@echo "  Full Ref:     $(IMAGE_REF)"
	@echo "  Local:        $(IMAGE_LOCAL)"
	@echo "  Base Image:   $(BASE_IMAGE)"
	@echo ""
	@echo "  \033[1mHelm:\033[0m"
	@echo "  ─────────────────────────────────────"
	@echo "  Chart:        $(HELM_CHART)"
	@echo "  Release:      $(HELM_RELEASE)"
	@echo "  Namespace:    $(HELM_NAMESPACE)"
	@echo "  Values:       $(HELM_VALUES)"
	@echo ""
	@echo "  \033[2mExamples:\033[0m"
	@echo "    make build TAG=1.0.0"
	@echo "    make push TAG=1.0.0 REGISTRY=ghcr.io NAMESPACE=myuser"
	@echo "    make helm-install HELM_NAMESPACE=my-ns"
	@echo ""

# ============================================================================
#  Helm Operations
# ============================================================================

helm-lint:
	@echo "Linting Helm chart..."
	@helm lint $(HELM_CHART)
	@echo "\033[32m✓ Chart linted successfully\033[0m"

helm-template:
	@echo "Rendering Helm templates..."
	@helm template $(HELM_RELEASE) $(HELM_CHART) \
		--namespace $(HELM_NAMESPACE) \
		-f $(HELM_VALUES)

helm-dry-run:
	@echo "Dry-run Helm install..."
	@helm install $(HELM_RELEASE) $(HELM_CHART) \
		--namespace $(HELM_NAMESPACE) \
		--create-namespace \
		-f $(HELM_VALUES) \
		--dry-run --debug

helm-install:
	@echo "Installing Helm chart..."
	@helm install $(HELM_RELEASE) $(HELM_CHART) \
		--namespace $(HELM_NAMESPACE) \
		--create-namespace \
		-f $(HELM_VALUES)
	@echo "\033[32m✓ Chart installed: $(HELM_RELEASE)\033[0m"

helm-upgrade:
	@echo "Upgrading Helm release..."
	@helm upgrade $(HELM_RELEASE) $(HELM_CHART) \
		--namespace $(HELM_NAMESPACE) \
		-f $(HELM_VALUES) \
		--install
	@echo "\033[32m✓ Chart upgraded: $(HELM_RELEASE)\033[0m"

helm-uninstall:
	@echo "Uninstalling Helm release..."
	@helm uninstall $(HELM_RELEASE) --namespace $(HELM_NAMESPACE)
	@echo "\033[32m✓ Chart uninstalled: $(HELM_RELEASE)\033[0m"

helm-status:
	@helm status $(HELM_RELEASE) --namespace $(HELM_NAMESPACE)

helm-package:
	@echo "Packaging Helm chart..."
	@helm package $(HELM_CHART)
	@echo "\033[32m✓ Chart packaged\033[0m"

helm-clean:
	@echo "Cleaning packaged charts..."
	@rm -f *.tgz
	@echo "\033[32m✓ Cleaned\033[0m"
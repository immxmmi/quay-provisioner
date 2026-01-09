# ======================
# Image / Registry
# ======================
REGISTRY ?= docker.io
NAMESPACE ?= test
IMAGE_NAME ?= quay-provisioner
VERSION ?= 0.0.2

IMAGE_REF := $(REGISTRY)/$(NAMESPACE)/$(IMAGE_NAME):$(VERSION)

help:
	@echo "======================================"
	@echo " PipelineExecutionPlatform - Makefile "
	@echo "======================================"
	@echo "Available targets:"
	@echo ""
	@echo "  --- Python Development ---"
	@echo "  run                        Run the pipeline locally"
	@echo "  run-debug                  Run the pipeline with debug output"
	@echo "  test                       Run syntax checks and unit tests"
	@echo "  lint                       Run linting with ruff"
	@echo "  lint-fix                   Run linting and auto-fix issues"
	@echo "  check                      Run all checks (lint + test)"
	@echo "  clean                      Remove cache files and __pycache__"
	@echo ""
	@echo "  --- Docker & Environment ---"
	@echo "  install_quay_environment   Start local Quay test environment"
	@echo "  deinstall_quay_environment Stop and remove Quay test environment"
	@echo "  build_image                Build normal Docker image"
	@echo "  build_offline              Build offline Docker image (uses wheelhouse)"
	@echo "  run_image                  Run the Docker image interactively"
	@echo "  export_image               Export the Docker image to a tar file"
	@echo "  create_wheelhouse          Build Python wheels for offline builds"
	@echo "  clean_wheelhouse           Clean the wheelhouse directory"
	@echo "  check_python_version       Check Python version in the Docker image"

	@echo "Docker Image Push Targets:"
	@echo "  login_registry             Log in to the container registry"
	@echo "  build_image                Build the Docker image using buildah"
	@echo "  push_image                 Push the Docker image to the registry"

	@echo ""
	@echo "Usage:"
	@echo "  make <target>"
	@echo "======================================"


PYTHON     ?= python
SRC_DIR    := src
PY_VERSION ?= 3.12
IMAGE      ?= quay.io/lib/python:$(PY_VERSION)
REGISTRY   ?= quay.io
REPO	   ?= your-repo/quay-provisioner
TAG		   ?= latest

# ======================
# Python Development
# ======================

run:
	@echo "Running pipeline..."
	cd $(SRC_DIR) && $(PYTHON) main.py

run-debug:
	@echo "Running pipeline with debug output..."
	cd $(SRC_DIR) && DEBUG_ENABLED=true $(PYTHON) main.py

test:
	@echo "=== Syntax Check ==="
	@cd $(SRC_DIR) && $(PYTHON) -m py_compile \
		exceptions.py \
		actions/base_action.py \
		config/loader.py \
		gateway/client.py \
		gateway/quay_gateway.py \
		engine/pipeline_engine.py \
		engine/pipeline_executor.py \
		engine_reader/pipeline_reader.py \
		actions/create_organization.py \
		actions/delete_organization.py \
		actions/get_organization.py \
		actions/list_organizations.py \
		actions/create_robot_account.py \
		actions/delete_robot_account.py \
		actions/get_robot_account.py \
		actions/list_robot_accounts.py
	@echo "✓ Syntax check passed"
	@echo ""
	@echo "=== Import Tests ==="
	@cd $(SRC_DIR) && $(PYTHON) -c "from exceptions import PipelineError, QuayApiError, ValidationError; print('✓ exceptions')"
	@cd $(SRC_DIR) && $(PYTHON) -c "from actions.base_action import BaseAction; print('✓ base_action')"
	@cd $(SRC_DIR) && $(PYTHON) -c "from actions.create_organization import CreateOrganizationAction; print('✓ actions')"
	@cd $(SRC_DIR) && $(PYTHON) -c "from config.loader import Config; print('✓ config')"
	@echo ""
	@echo "=== Unit Tests ==="
	@cd $(SRC_DIR) && $(PYTHON) -c "\
from config.loader import Config; \
c1 = Config(); c2 = Config(); \
assert c1 is c2, 'Singleton failed'; \
print('✓ Config singleton'); \
Config.reset()"
	@cd $(SRC_DIR) && $(PYTHON) -c "\
from gateway.client import ApiClient; \
client = ApiClient(); \
masked = client._mask_sensitive_headers({'Authorization': 'secret', 'Content-Type': 'json'}); \
assert masked['Authorization'] == '***REDACTED***'; \
print('✓ Header masking')"
	@cd $(SRC_DIR) && $(PYTHON) -c "\
from gateway.quay_gateway import _safe_path; \
assert _safe_path('test/path') == 'test%2Fpath'; \
print('✓ URL encoding')"
	@echo ""
	@echo "=== All tests passed! ==="

lint:
	@which ruff > /dev/null 2>&1 && ruff check $(SRC_DIR) || echo "ruff not installed. Run: pip install ruff"

lint-fix:
	@which ruff > /dev/null 2>&1 && ruff check $(SRC_DIR) --fix || echo "ruff not installed. Run: pip install ruff"

check: lint test

clean:
	@echo "Cleaning cache files..."
	@find $(SRC_DIR) -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find $(SRC_DIR) -type f -name "*.pyc" -delete 2>/dev/null || true
	@find $(SRC_DIR) -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "✓ Cleaned"

# ======================
# Docker & Environment
# ======================

install_quay_environment:
	@echo "Installing Quay environment..."
	docker compose -f environment/quay/docker-compose.yaml up -d
	@echo "Quay environment installed."

deinstall_quay_environment:
	@echo "Removing Quay environment..."
	docker compose -f environment/quay/docker-compose.yaml down
	@echo "Quay environment removed."

check_python_version:
	@echo "Checking Python version in Docker image..."
	docker run --rm $(IMAGE) python --version
	@echo "Python version checked."

create_wheelhouse:
	mkdir -p wheels
	docker run --rm \
	  -v "$(PWD)/requirements.txt:/requirements.txt" \
	  -v "$(PWD)/wheels:/wheels" \
	  $(IMAGE) \
	  sh -c "pip install --upgrade pip && \
	         pip download --only-binary=:all: -r /requirements.txt -d /wheels"
	@echo "✓ Wheelhouse created in ./wheels"

clean_wheelhouse:
	rm -rf wheels
	mkdir wheels
	@echo "✓ Wheelhouse cleaned"

build_image:
	@echo "Building Docker image..."
	docker build -t quay-provisioner .
	@echo "Docker image built."

download_image:
	skopeo copy \
  --override-os linux \
  --override-arch amd64 \
  docker://ghcr.io/immxmmi/quay-provisioner:0.1.0-6408c92 \
  docker-archive:quay-provisioner.tar

export_image: build_image
	@echo "Exporting Docker image quay-provisioner..."
	docker save quay-provisioner -o quay-provisioner.tar
	@echo "✓ Image exported to quay-provisioner.tar"

push_image:
	@echo "Pushing Docker image to $(REGISTRY)..."
	docker tag quay-provisioner $(REGISTRY)/$(REPO):$(TAG)
	docker push $(REGISTRY)/$(REPO):$(TAG)
	@echo "✓ Image pushed to $(REGISTRY)/$(REPO)"

build_offline:
	@echo "Building offline Docker image..."
	docker build -f Dockerfile_offline -t quay-provisioner-offline .
	@echo "Offline Docker image built."

run_image:
	@echo "Running Docker image (interactive with host network)..."
	docker run --rm -it \
		--network host \
		-v $(PWD)/src/pipelines:/app/pipelines \
		quay-provisioner

run_offline:
	@echo "Running OFFLINE Docker image (interactive with host network)..."
	docker run --rm -it \
		--network host \
		-v $(PWD)/src/pipelines:/app/pipelines \
		quay-provisioner-offline

login_registry:
	@echo "Logging in to $(REGISTRY)..."
	buildah login $(REGISTRY)

build_image:
	@echo "Building image with buildah..."
	buildah bud -f Dockerfile -t $(IMAGE_REF) .
	@echo "✓ Image built: $(IMAGE_REF)"

push_image: login_registry
	@echo "Pushing image to $(IMAGE_REF)..."
	buildah push $(IMAGE_REF)
	@echo "✓ Image pushed"
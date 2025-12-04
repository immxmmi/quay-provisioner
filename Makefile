help:
	@echo "======================================"
	@echo " PipelineExecutionPlatform - Makefile "
	@echo "======================================"
	@echo "Available targets:"
	@echo ""
	@echo "  help                       Show this help message"
	@echo "  install_quay_environment   Start local Quay test environment"
	@echo "  deinstall_quay_environment Stop and remove Quay test environment"
	@echo "  create_wheelhouse          Build Python wheels for offline builds"
	@echo "  clean_wheelhouse           Clean the wheelhouse directory"
	@echo "  build_image                Build normal Docker image"
	@echo "  build_offline              Build offline Docker image (uses wheelhouse)"
	@echo ""
	@echo "Usage:"
	@echo "  make <target>"
	@echo "======================================"


PY_VERSION ?= 3.12
IMAGE      ?= python:$(PY_VERSION)-slim


install_quay_environment:
	@echo "Installing Quay environment..."
	docker compose -f environment/quay/docker-compose.yaml up -d
	@echo "Quay environment installed."

deinstall_quay_environment:
	@echo "Removing Quay environment..."
	docker compose -f environment/quay/docker-compose.yaml down
	@echo "Quay environment removed."

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
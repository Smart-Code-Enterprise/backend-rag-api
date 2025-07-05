# Makefile for RAG Backend API Docker Operations
# Registry: docker-registry.imutably.com

# Configuration
REGISTRY := docker-registry.imutably.com/v2
IMAGE_NAME := smartcodes-backend
VERSION ?= $(shell git describe --tags --always --dirty 2>/dev/null || echo "latest")
BUILD_DATE := $(shell date -u +'%Y-%m-%dT%H:%M:%SZ')
GIT_COMMIT := $(shell git rev-parse --short HEAD 2>/dev/null || echo "unknown")

# Docker image tags
IMAGE_TAG := $(REGISTRY)/$(IMAGE_NAME):$(VERSION)
IMAGE_TAG_LATEST := $(REGISTRY)/$(IMAGE_NAME):latest
IMAGE_TAG_COMMIT := $(REGISTRY)/$(IMAGE_NAME):$(GIT_COMMIT)

# Build arguments
DOCKER_BUILD_ARGS := \
	--build-arg BUILD_DATE=$(BUILD_DATE) \
	--build-arg VERSION=$(VERSION) \
	--build-arg GIT_COMMIT=$(GIT_COMMIT)

# Default target
.PHONY: help
help: ## Show this help message
	@echo "Available targets:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Build targets
.PHONY: build
build: ## Build Docker image with version tag
	docker build $(DOCKER_BUILD_ARGS) -t $(IMAGE_TAG) .
	@echo "Built image: $(IMAGE_TAG)"

.PHONY: build-latest
build-latest: ## Build Docker image with latest tag
	docker build $(DOCKER_BUILD_ARGS) -t $(IMAGE_TAG_LATEST) .
	@echo "Built image: $(IMAGE_TAG_LATEST)"

.PHONY: build-commit
build-commit: ## Build Docker image with git commit tag
	docker build $(DOCKER_BUILD_ARGS) -t $(IMAGE_TAG_COMMIT) .
	@echo "Built image: $(IMAGE_TAG_COMMIT)"

.PHONY: build-all
build-all: build build-latest build-commit ## Build all image variants

# Push targets
.PHONY: push
push: ## Push versioned image to registry
	docker push $(IMAGE_TAG)
	@echo "Pushed image: $(IMAGE_TAG)"

.PHONY: push-latest
push-latest: ## Push latest image to registry
	docker push $(IMAGE_TAG_LATEST)
	@echo "Pushed image: $(IMAGE_TAG_LATEST)"

.PHONY: push-commit
push-commit: ## Push commit-tagged image to registry
	docker push $(IMAGE_TAG_COMMIT)
	@echo "Pushed image: $(IMAGE_TAG_COMMIT)"

.PHONY: push-all
push-all: push push-latest push-commit ## Push all image variants

# Build and push targets
.PHONY: build-push
build-push: build push ## Build and push versioned image

.PHONY: build-push-latest
build-push-latest: build-latest push-latest ## Build and push latest image

.PHONY: build-push-commit
build-push-commit: build-commit push-commit ## Build and push commit-tagged image

.PHONY: build-push-all
build-push-all: build-all push-all ## Build and push all image variants

# Development targets
.PHONY: dev-build
dev-build: ## Build development image (no cache)
	docker build --no-cache $(DOCKER_BUILD_ARGS) -t $(IMAGE_TAG) .
	@echo "Built development image: $(IMAGE_TAG)"

.PHONY: run
run: ## Run the container locally
	docker run -p 8000:8000 \
		-e OPENAI_API_KEY=$${OPENAI_API_KEY} \
		-e HOST=0.0.0.0 \
		-e PORT=8000 \
		-e LOG_LEVEL=INFO \
		$(IMAGE_TAG)

.PHONY: run-latest
run-latest: ## Run the latest container locally
	docker run -p 18000:8000 \
		-e OPENAI_API_KEY=$${OPENAI_API_KEY} \
		-e HOST=0.0.0.0 \
		-e PORT=8000 \
		-e LOG_LEVEL=INFO \
		$(IMAGE_TAG_LATEST)

# Cleanup targets
.PHONY: clean
clean: ## Remove local Docker images
	docker rmi $(IMAGE_TAG) $(IMAGE_TAG_LATEST) $(IMAGE_TAG_COMMIT) 2>/dev/null || true
	@echo "Cleaned up local images"

.PHONY: clean-all
clean-all: ## Remove all related Docker images and containers
	docker stop $$(docker ps -q --filter ancestor=$(IMAGE_TAG)) 2>/dev/null || true
	docker stop $$(docker ps -q --filter ancestor=$(IMAGE_TAG_LATEST)) 2>/dev/null || true
	docker stop $$(docker ps -q --filter ancestor=$(IMAGE_TAG_COMMIT)) 2>/dev/null || true
	docker rmi $$(docker images -q $(REGISTRY)/$(IMAGE_NAME)) 2>/dev/null || true
	@echo "Cleaned up all related images and containers"

# Utility targets
.PHONY: info
info: ## Show build information
	@echo "Registry: $(REGISTRY)"
	@echo "Image Name: $(IMAGE_NAME)"
	@echo "Version: $(VERSION)"
	@echo "Git Commit: $(GIT_COMMIT)"
	@echo "Build Date: $(BUILD_DATE)"
	@echo ""
	@echo "Image Tags:"
	@echo "  Version: $(IMAGE_TAG)"
	@echo "  Latest: $(IMAGE_TAG_LATEST)"
	@echo "  Commit: $(IMAGE_TAG_COMMIT)"

.PHONY: test
test: ## Run tests (placeholder - add your test commands here)
	@echo "Running tests..."
	# Add your test commands here
	# Example: python -m pytest tests/

.PHONY: lint
lint: ## Run linting (placeholder - add your lint commands here)
	@echo "Running linting..."
	# Add your lint commands here
	# Example: flake8 . --max-line-length=88

# Docker Compose targets
.PHONY: compose-up
compose-up: ## Start services with docker-compose
	docker-compose up -d

.PHONY: compose-down
compose-down: ## Stop services with docker-compose
	docker-compose down

.PHONY: compose-logs
compose-logs: ## Show docker-compose logs
	docker-compose logs -f

.PHONY: compose-build
compose-build: ## Build services with docker-compose
	docker-compose build

# Security scanning
.PHONY: scan
scan: ## Scan Docker image for vulnerabilities
	docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
		-v $$(pwd):/workspace \
		--workdir /workspace \
		anchore/grype:latest $(IMAGE_TAG)

# Production deployment helpers
.PHONY: deploy-staging
deploy-staging: build-push-latest ## Deploy to staging (build and push latest)
	@echo "Deployed to staging: $(IMAGE_TAG_LATEST)"

.PHONY: deploy-production
deploy-production: build-push ## Deploy to production (build and push versioned)
	@echo "Deployed to production: $(IMAGE_TAG)"

# Quick development workflow
.PHONY: dev
dev: dev-build run ## Quick development workflow: build and run

# Docker Registry Authentication
.PHONY: docker-login
docker-login: ## Login to Docker registry
	@echo "Logging into Docker registry: $(REGISTRY)"
	@if [ -n "$(DOCKER_USERNAME)" ] && [ -n "$(DOCKER_PASSWORD)" ]; then \
		echo "Using environment variables for user: $(DOCKER_USERNAME)"; \
		echo "$(DOCKER_PASSWORD)" | docker login "$(REGISTRY)" -u "$(DOCKER_USERNAME)" --password-stdin; \
	else \
		echo "Please enter your credentials for $(REGISTRY)"; \
		docker login "$(REGISTRY)"; \
	fi
	@echo "Successfully logged into $(REGISTRY)"

# Default target
.DEFAULT_GOAL := help 
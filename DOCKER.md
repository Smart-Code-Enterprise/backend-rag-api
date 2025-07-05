# Docker Operations Guide

This guide explains how to build, push, and manage Docker images for the RAG Backend API using the provided Makefile.

## Prerequisites

- Docker installed and running
- Access to `docker-registry.imutably.com`
- Git repository with proper tagging (for version management)

## Quick Start

### 1. Login to Docker Registry

```bash
# Interactive login
./scripts/docker-login.sh

# Or with credentials
./scripts/docker-login.sh your-username your-password

# Or using environment variables
export DOCKER_USERNAME=your-username
export DOCKER_PASSWORD=your-password
./scripts/docker-login.sh
```

### 2. Build and Push

```bash
# Build and push versioned image (recommended for production)
make build-push

# Build and push latest image (for staging/development)
make build-push-latest

# Build and push all variants
make build-push-all
```

## Makefile Targets

### Build Targets

- `make build` - Build image with version tag
- `make build-latest` - Build image with latest tag
- `make build-commit` - Build image with git commit tag
- `make build-all` - Build all image variants
- `make dev-build` - Build without cache (for development)

### Push Targets

- `make push` - Push versioned image to registry
- `make push-latest` - Push latest image to registry
- `make push-commit` - Push commit-tagged image to registry
- `make push-all` - Push all image variants

### Combined Targets

- `make build-push` - Build and push versioned image
- `make build-push-latest` - Build and push latest image
- `make build-push-commit` - Build and push commit-tagged image
- `make build-push-all` - Build and push all variants

### Development Targets

- `make run` - Run the container locally
- `make run-latest` - Run the latest container locally
- `make dev` - Quick development workflow (build and run)

### Utility Targets

- `make help` - Show all available targets
- `make info` - Show build information
- `make clean` - Remove local Docker images
- `make clean-all` - Remove all related images and containers

### Docker Compose Targets

- `make compose-up` - Start services with docker-compose
- `make compose-down` - Stop services with docker-compose
- `make compose-logs` - Show docker-compose logs
- `make compose-build` - Build services with docker-compose

### Security and Quality

- `make scan` - Scan Docker image for vulnerabilities
- `make test` - Run tests (placeholder)
- `make lint` - Run linting (placeholder)

## Image Tagging Strategy

The Makefile uses a comprehensive tagging strategy:

1. **Version Tags**: Based on git tags (e.g., `v1.0.0`)
2. **Latest Tag**: Always points to the most recent build
3. **Commit Tags**: Based on git commit hash for traceability

### Examples

```bash
# If you have a git tag v1.2.3
make build-push
# Creates: docker-registry.imutably.com/rag-backend-api:v1.2.3

# Latest build
make build-push-latest
# Creates: docker-registry.imutably.com/rag-backend-api:latest

# Commit-based build
make build-push-commit
# Creates: docker-registry.imutably.com/rag-backend-api:a1b2c3d
```

## Environment Variables

The Makefile uses these environment variables:

- `VERSION` - Override the version (defaults to git tag)
- `DOCKER_USERNAME` - Registry username
- `DOCKER_PASSWORD` - Registry password
- `OPENAI_API_KEY` - Required for running the container

## Production Deployment

### Staging Deployment

```bash
make deploy-staging
# Builds and pushes latest tag
```

### Production Deployment

```bash
# First, create a git tag
git tag v1.0.0
git push origin v1.0.0

# Then deploy
make deploy-production
# Builds and pushes versioned tag
```

## Security Best Practices

1. **Scan Images**: Use `make scan` to check for vulnerabilities
2. **Use Specific Tags**: Prefer versioned tags over `latest` in production
3. **Regular Updates**: Keep base images and dependencies updated
4. **Secrets Management**: Use environment variables for sensitive data

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   ```bash
   # Re-login to registry
   ./scripts/docker-login.sh
   ```

2. **Build Fails**
   ```bash
   # Clean and rebuild
   make clean
   make dev-build
   ```

3. **Push Fails**
   ```bash
   # Check if you're logged in
   docker login docker-registry.imutably.com
   ```

### Debug Information

```bash
# Show build information
make info

# Check Docker images
docker images | grep rag-backend-api

# Check running containers
docker ps | grep rag-backend-api
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build and Push Docker Image

on:
  push:
    tags: ['v*']

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Login to Docker Registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login docker-registry.imutably.com -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
      
      - name: Build and Push
        run: make build-push
```

### GitLab CI Example

```yaml
build_and_push:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  variables:
    DOCKER_TLS_CERTDIR: "/certs"
  before_script:
    - echo $DOCKER_PASSWORD | docker login docker-registry.imutably.com -u $DOCKER_USERNAME --password-stdin
  script:
    - make build-push
  only:
    - tags
```

## Performance Optimization

1. **Use .dockerignore**: Excludes unnecessary files from build context
2. **Layer Caching**: Requirements are installed before copying code
3. **Multi-stage Builds**: Consider for production optimization
4. **Image Size**: Uses Python slim base image

## Monitoring and Logging

The container includes:
- Health checks on `/health` endpoint
- Structured logging
- Environment-based log levels

```bash
# Check container health
docker inspect --format='{{.State.Health.Status}}' container_name

# View logs
docker logs container_name
``` 
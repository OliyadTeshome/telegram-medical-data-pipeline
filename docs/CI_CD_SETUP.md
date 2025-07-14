# CI/CD Setup Documentation

This document describes the CI/CD pipeline setup for the Telegram Medical Data Pipeline project.

## Overview

The project uses GitHub Actions for continuous integration and deployment with the following workflows:

1. **CI Pipeline** (`ci.yml`) - Code quality, testing, and building
2. **Security Scanning** (`security.yml`) - Dependency and container security
3. **Deployment** (`deploy.yml`) - Docker image building and deployment

## Workflow Details

### 1. CI Pipeline (`ci.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

**Jobs:**

#### Code Quality & Linting
- **Code formatting check** using Black and isort
- **Linting** using flake8
- **Type checking** using mypy

#### Unit Tests
- **Test execution** with pytest
- **Coverage reporting** with pytest-cov
- **PostgreSQL service** for integration tests
- **Coverage upload** to Codecov

#### Build
- **Docker image building**
- **Image testing**
- **Artifact caching**

### 2. Security Scanning (`security.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches
- Weekly scheduled scan (Mondays at 2 AM)

**Jobs:**

#### Dependency Security Scan
- **Safety check** for Python dependencies
- **Vulnerability reporting**

#### Container Security Scan
- **Trivy vulnerability scanner**
- **SARIF report generation**
- **GitHub Security tab integration**

#### Secrets Scanning
- **TruffleHog** for secret detection
- **Pre-commit scanning**

### 3. Deployment (`deploy.yml`)

**Triggers:**
- Push to `main` branch
- Tag pushes (v* pattern)

**Jobs:**

#### Build and Deploy
- **Docker image building**
- **Container Registry login** (GitHub Container Registry)
- **Image tagging** with semantic versioning
- **Image pushing** to registry

## Configuration Files

### Code Quality Tools

#### `pyproject.toml`
- **Black configuration** for code formatting
- **isort configuration** for import sorting
- **mypy configuration** for type checking
- **pytest configuration** for testing
- **coverage configuration** for test coverage

#### `.flake8`
- **Flake8 configuration** for linting
- **Line length** set to 88 (Black compatible)
- **Complexity limits** and exclusions

### Docker Configuration

#### `.dockerignore`
- **Excludes unnecessary files** from Docker build context
- **Optimizes build performance**
- **Prevents sensitive data** from being included

### Dependency Management

#### `dependabot.yml`
- **Automated dependency updates**
- **Weekly schedule** for updates
- **Pull request creation** for updates

## Environment Variables

### Required Secrets

The following secrets should be configured in your GitHub repository:

```bash
# For deployment to GitHub Container Registry
GITHUB_TOKEN  # Automatically provided by GitHub

# For external services (if needed)
DOCKER_REGISTRY_USERNAME
DOCKER_REGISTRY_PASSWORD
```

### Environment Configuration

The workflows use the following environment variables:

```yaml
env:
  PYTHON_VERSION: '3.11'
  POSTGRES_VERSION: '15'
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}
```

## Testing Strategy

### Unit Tests
- **Location**: `tests/` directory
- **Framework**: pytest
- **Coverage**: pytest-cov
- **Async support**: pytest-asyncio

### Integration Tests
- **PostgreSQL service** in CI
- **Mock external services**
- **Test database** isolation

### Test Structure
```
tests/
├── __init__.py
├── test_scraper.py
├── test_loader.py
└── conftest.py  # Shared fixtures
```

## Security Measures

### Dependency Scanning
- **Safety** for Python package vulnerabilities
- **Weekly automated scans**
- **JSON report generation**

### Container Security
- **Trivy** for container vulnerability scanning
- **SARIF format** for GitHub integration
- **Base image scanning**

### Secrets Detection
- **TruffleHog** for secret scanning
- **Pre-commit hooks** (recommended)
- **Historical scanning**

## Deployment Strategy

### Container Registry
- **GitHub Container Registry** (ghcr.io)
- **Automatic authentication** with GITHUB_TOKEN
- **Semantic versioning** support

### Image Tagging
- **Branch-based tags** for development
- **Semantic version tags** for releases
- **SHA-based tags** for debugging

### Build Optimization
- **Docker layer caching**
- **Multi-stage builds** (if needed)
- **Build context optimization**

## Monitoring and Alerts

### Workflow Notifications
- **Email notifications** for failures
- **Slack integration** (if configured)
- **Status badges** for README

### Security Alerts
- **GitHub Security tab** integration
- **Dependabot alerts**
- **Container vulnerability reports**

## Best Practices

### Code Quality
1. **Run local checks** before pushing:
   ```bash
   black --check .
   isort --check-only .
   flake8 .
   mypy src/
   pytest tests/
   ```

2. **Pre-commit hooks** (recommended):
   ```bash
   pip install pre-commit
   pre-commit install
   ```

### Security
1. **Regular dependency updates**
2. **Container base image updates**
3. **Secret rotation**
4. **Access control review**

### Deployment
1. **Test in staging** before production
2. **Rollback strategy** preparation
3. **Health check** implementation
4. **Monitoring** setup

## Troubleshooting

### Common Issues

#### Build Failures
- **Check Dockerfile** syntax
- **Verify dependencies** in requirements.txt
- **Review build logs** for errors

#### Test Failures
- **Check test database** connectivity
- **Verify mock configurations**
- **Review test data** setup

#### Security Scan Failures
- **Update vulnerable dependencies**
- **Review container base images**
- **Check for hardcoded secrets**

### Debugging

#### Local Testing
```bash
# Run CI checks locally
black --check .
isort --check-only .
flake8 .
mypy src/
pytest tests/ -v
```

#### Docker Testing
```bash
# Build and test Docker image
docker build -t test-image .
docker run --rm test-image python -c "import sys; print('OK')"
```

## Future Enhancements

### Planned Improvements
1. **Multi-environment deployment** (staging/production)
2. **Performance testing** integration
3. **Load testing** for API endpoints
4. **Database migration** testing
5. **Rollback automation**

### Monitoring Integration
1. **Application performance monitoring**
2. **Error tracking** (Sentry)
3. **Log aggregation** (ELK stack)
4. **Metrics collection** (Prometheus)

## Support

For issues with the CI/CD pipeline:

1. **Check workflow logs** in GitHub Actions
2. **Review configuration files**
3. **Test locally** using provided commands
4. **Create issue** with detailed error information

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Python Testing Guide](https://docs.pytest.org/)
- [Security Best Practices](https://owasp.org/www-project-top-ten/) 
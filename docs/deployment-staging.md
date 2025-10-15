# Staging Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the AI Agent MCP Server to a staging environment and validating production readiness.

**Target Environment:** Staging (production-like)
**Container Runtime:** Podman (compatible with Docker)
**Deployment Approach:** Manual deployment for validation (automated deployment via CI/CD in future)

## Prerequisites

- Production container image built and tested locally
- Access to staging environment (container runtime: Podman or Kubernetes)
- Staging database configured (PostgreSQL with pgvector extension)
- Container registry access (Docker Hub or ghcr.io)
- Staging environment variables configured

## Deployment Process

### 1. Build Production Container Image

Build the production container image with staging tag:

```bash
# Build container with staging tag
task container:build TAG=staging-v0.1.0

# Verify image created successfully
podman images | grep mcp-server
```

**Expected Output:**
```
localhost/mcp-server  staging-v0.1.0  <image-id>  <timestamp>  ~230 MB
```

### 2. Push Container Image to Registry

Push the container image to a container registry for staging environment access:

```bash
# Tag image for registry (Docker Hub example)
podman tag localhost/mcp-server:staging-v0.1.0 your-dockerhub-username/mcp-server:staging-v0.1.0

# Login to registry
podman login docker.io

# Push image to registry
podman push your-dockerhub-username/mcp-server:staging-v0.1.0
```

**Alternative: GitHub Container Registry (ghcr.io)**
```bash
# Tag image for ghcr.io
podman tag localhost/mcp-server:staging-v0.1.0 ghcr.io/your-org/mcp-server:staging-v0.1.0

# Login to GitHub Container Registry
echo $GITHUB_TOKEN | podman login ghcr.io -u your-github-username --password-stdin

# Push image to ghcr.io
podman push ghcr.io/your-org/mcp-server:staging-v0.1.0
```

### 3. Configure Staging Environment Variables

Create `.env.staging` file with staging-specific configuration:

```bash
# Application Configuration - Staging Environment
APP_NAME="AI Agent MCP Server"
APP_VERSION="0.1.0"
DEBUG=false

# Server Configuration
HOST="0.0.0.0"
PORT=8000

# Database Configuration
DATABASE_URL="postgresql+asyncpg://mcp_user:staging_password@staging-db-host:5432/mcp_staging"

# Logging Configuration
LOG_LEVEL="INFO"
LOG_FORMAT="json"

# Environment identifier
ENVIRONMENT="staging"
```

**Security Note:** Never commit `.env.staging` to version control. Store credentials securely (e.g., Kubernetes Secrets, Vault).

### 4. Deploy Container to Staging Environment

#### Option A: Podman Deployment (Local or Remote Host)

```bash
# Pull image from registry on staging host
podman pull your-dockerhub-username/mcp-server:staging-v0.1.0

# Run container with staging configuration
podman run -d \
  --name mcp-server-staging \
  -p 8000:8000 \
  --env-file .env.staging \
  --health-cmd "curl -f http://localhost:8000/health || exit 1" \
  --health-interval 30s \
  --health-timeout 10s \
  --health-retries 3 \
  your-dockerhub-username/mcp-server:staging-v0.1.0

# Verify container is running
podman ps | grep mcp-server-staging
```

#### Option B: Kubernetes Deployment (Future - EPIC-005)

```bash
# Apply Kubernetes manifests (deferred to EPIC-005)
kubectl apply -f k8s/staging/deployment.yaml
kubectl apply -f k8s/staging/service.yaml
kubectl apply -f k8s/staging/configmap.yaml
```

### 5. Verify Deployment Status

Check that container started successfully:

```bash
# Check container status
podman ps -a | grep mcp-server-staging

# Check container logs
podman logs mcp-server-staging

# Check container health
podman healthcheck run mcp-server-staging
```

**Expected Log Output:**
```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 6. Execute Validation Tests

Run the validation checklist (see next section) to confirm production readiness.

## Validation Checklist

Complete all validation steps to confirm staging deployment successful:

### Container Deployment Validation

- [ ] **Container starts successfully**
  ```bash
  podman ps | grep mcp-server-staging
  # Expected: Container shows "Up" status
  ```

- [ ] **No errors in container logs**
  ```bash
  podman logs mcp-server-staging | grep -i error
  # Expected: No unexpected error messages
  ```

### Health Check Validation

- [ ] **Health check endpoint responds with 200 OK**
  ```bash
  curl -v http://staging-host:8000/health
  # Expected: HTTP/1.1 200 OK
  ```

- [ ] **Health check response contains system information**
  ```bash
  curl http://staging-host:8000/health | jq
  # Expected: JSON with status, version, timestamp
  ```

- [ ] **Health check response time acceptable (<2 seconds)**
  ```bash
  time curl http://staging-host:8000/health
  # Expected: real time < 2 seconds
  ```

### Application Behavior Validation

- [ ] **Application serves requests correctly**
  ```bash
  curl http://staging-host:8000/
  # Expected: JSON response with API information
  ```

- [ ] **Application behavior matches local development**
  - Test core API endpoints
  - Verify response formats identical to local
  - No environment-specific bugs discovered

### Configuration Validation

- [ ] **Environment variables loaded correctly**
  ```bash
  podman exec mcp-server-staging env | grep APP_NAME
  podman exec mcp-server-staging env | grep LOG_LEVEL
  # Expected: Staging environment variables present
  ```

- [ ] **Database connection configured correctly** (if applicable)
  ```bash
  # Check database connectivity via application logs or health endpoint
  podman logs mcp-server-staging | grep -i database
  ```

### Performance Validation

- [ ] **Application startup time meets requirements (<10 seconds)**
  ```bash
  # Stop container
  podman stop mcp-server-staging

  # Start container and measure time
  time podman start mcp-server-staging

  # Wait for health check to pass
  sleep 5
  curl http://staging-host:8000/health
  # Expected: Startup + health check < 10 seconds total
  ```

- [ ] **Response times comparable to local development**
  ```bash
  # Benchmark health endpoint
  ab -n 100 -c 10 http://staging-host:8000/health
  # Expected: Average response time reasonable (< 100ms)
  ```

### Reliability Validation

- [ ] **Container restart works correctly**
  ```bash
  # Restart container
  podman restart mcp-server-staging

  # Verify container returns to healthy state
  sleep 5
  podman ps | grep mcp-server-staging
  curl http://staging-host:8000/health
  # Expected: Container running, health check passes
  ```

- [ ] **Container logs accessible**
  ```bash
  podman logs mcp-server-staging
  # Expected: Logs show startup and request handling
  ```

### Team Review

- [ ] **Product Owner confirms behavior acceptable**
  - Core features work as expected
  - No regression or unexpected behavior

- [ ] **Tech Lead confirms technical implementation ready**
  - Container configuration sound
  - Performance acceptable
  - No technical blockers identified

- [ ] **DevOps confirms deployment process sound**
  - Deployment steps clear and repeatable
  - Rollback procedure tested
  - Monitoring and logging adequate

- [ ] **Team agrees to proceed with production deployment**
  - All validation criteria met
  - Production readiness confirmed

## Rollback Procedure

If staging deployment fails or issues discovered:

### 1. Stop and Remove Failed Container

```bash
# Stop container
podman stop mcp-server-staging

# Remove container
podman rm mcp-server-staging
```

### 2. Deploy Previous Version

```bash
# Deploy previous working version
podman run -d \
  --name mcp-server-staging \
  -p 8000:8000 \
  --env-file .env.staging \
  your-dockerhub-username/mcp-server:previous-version

# Verify rollback successful
curl http://staging-host:8000/health
```

### 3. Investigate and Fix Issues

- Review container logs: `podman logs mcp-server-staging`
- Check environment variables: `podman exec mcp-server-staging env`
- Test locally with identical configuration
- Fix issues and rebuild container image
- Retry deployment with new image

## Troubleshooting

### Container Won't Start

**Symptom:** Container exits immediately after starting

**Diagnosis:**
```bash
podman logs mcp-server-staging
# Check for startup errors
```

**Common Causes:**
- Missing or invalid environment variables
- Database connection failure
- Port already in use
- Application code error

**Solution:**
- Verify `.env.staging` file complete and valid
- Test database connectivity: `psql $DATABASE_URL`
- Check port availability: `netstat -tuln | grep 8000`
- Test container locally first: `task container:run`

### Health Check Failing

**Symptom:** Health check endpoint returns errors or timeouts

**Diagnosis:**
```bash
curl -v http://staging-host:8000/health
podman logs mcp-server-staging | tail -50
```

**Common Causes:**
- Application not fully started
- Health endpoint misconfigured
- Network routing issue

**Solution:**
- Wait for application startup (check logs for "Application startup complete")
- Verify health endpoint locally: `curl http://localhost:8000/health`
- Check network connectivity: `ping staging-host`

### Performance Issues

**Symptom:** Slow response times or high resource usage

**Diagnosis:**
```bash
# Check container resource usage
podman stats mcp-server-staging

# Benchmark endpoints
ab -n 100 -c 10 http://staging-host:8000/health
```

**Common Causes:**
- Insufficient resource limits
- Database query performance
- Network latency

**Solution:**
- Increase container resource limits (CPU, memory)
- Optimize database queries (add indexes, connection pooling)
- Profile application code for bottlenecks

## Next Steps

After successful staging validation:

1. **Document Deployment Results**
   - Record validation test results
   - Note any issues encountered and resolutions
   - Update deployment documentation with lessons learned

2. **Prepare for Production Deployment**
   - Create production environment configuration (`.env.production`)
   - Update deployment scripts for production environment
   - Plan production deployment schedule and rollback strategy

3. **Continuous Improvement**
   - Automate deployment process (CI/CD pipeline)
   - Implement monitoring and alerting (Prometheus, Grafana)
   - Add smoke tests to deployment pipeline

## Related Documentation

- **Container Build:** See `CLAUDE-tooling.md` Section "Container Management"
- **Environment Configuration:** See `.env.example` for all configuration options
- **CI/CD Pipeline:** See `.github/workflows/ci.yml` for automated builds
- **Production Deployment:** (To be created after staging validation)

---

**Document Version:** v1.0
**Last Updated:** 2025-10-15
**Author:** Context Engineering PoC Team
**Related Story:** US-025 (Validate Container Deployment in Staging)

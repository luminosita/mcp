# AI Agent MCP Server

[![CI/CD Pipeline](https://github.com/USERNAME/REPO/actions/workflows/ci.yml/badge.svg)](https://github.com/USERNAME/REPO/actions/workflows/ci.yml)

A Model Context Protocol (MCP) server implementation for AI agent interactions, built with FastAPI and Python 3.11+.

## Quick Start

### Prerequisites

- Python 3.11+
- Podman
- Git
- NuShell (for setup script)

### Setup

```bash
# Run automated setup script
nu scripts/setup.nu

# Or run in silent mode (CI/CD)
nu scripts/setup.nu --silent
```

### Development

```bash
# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows

# Run development server
task dev

# Run tests
task test

# Run linting
task lint
```

## Project Structure

```
project-root/
├── src/mcp_server/          # Main application package
│   ├── core/                # Core utilities and exceptions
│   ├── models/              # Data models
│   ├── services/            # Business logic
│   ├── repositories/        # Data access layer
│   ├── tools/               # MCP tools
│   ├── api/                 # FastAPI routes and schemas
│   └── utils/               # Utility functions
├── tests/                   # Test suite
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   └── e2e/                 # End-to-end tests
├── scripts/                 # Setup and utility scripts
└── docs/                    # Documentation

```

## Deployment

Container images are automatically built on all branches and pushed to GitHub Container Registry only on `release/*` branches. All container images are scanned for security vulnerabilities before deployment.

### Security Scanning

All container builds are automatically scanned for vulnerabilities using Trivy:

- **Scope:** CVEs in OS packages, Python dependencies, and base images
- **Severity Policy:**
  - **CRITICAL/HIGH:** Blocks deployment (build fails)
  - **MEDIUM/LOW:** Logged as warnings, deployment continues
- **Unfixed Vulnerabilities:** Ignored (no remediation available)
- **Scan Results:** Uploaded to GitHub Security tab for centralized tracking
- **Database Updates:** Trivy vulnerability database refreshed daily
- **Documented Exceptions:** Tracked in `.trivyignore` with risk assessments

View vulnerability reports: **Repository → Security → Code Scanning**

**Known Issues (.trivyignore):**
- CVE-2025-7709 (libsqlite3-0) - Awaiting Debian security update
- CVE-2025-8869 (pip) - Awaiting Python base image update

### Release Process

1. Create release branch: `git checkout -b release/v0.1.0`
2. Update version in `pyproject.toml`
3. Push to trigger automated build, security scan, and push: `git push -u origin release/v0.1.0`
4. Security scan validates image (blocks if CRITICAL/HIGH CVEs found)
5. Container image automatically pushed to `ghcr.io` with version tags (if scan passes)

### Using Pre-built Images

```bash
# Pull latest image
podman pull ghcr.io/USERNAME/REPO:latest

# Pull specific version
podman pull ghcr.io/USERNAME/REPO:0.1.0

# Pull by commit SHA
podman pull ghcr.io/USERNAME/REPO:abc123def

# Run container
podman run -d -p 8000:8000 ghcr.io/USERNAME/REPO:latest
```

### Building Locally

```bash
# Build with Taskfile
task container:build

# Build with custom tag
TAG=custom task container:build

# Run locally built image
task container:run
```

## Documentation

- [Setup Guide](docs/SETUP.md) - Detailed setup instructions
- [Architecture](docs/ARCHITECTURE.md) - System architecture
- [Contributing](docs/CONTRIBUTING.md) - Contribution guidelines
- [API Documentation](docs/API.md) - API reference

## Technology Stack

- **FastAPI** - Modern Python web framework
- **Pydantic** - Data validation
- **UV** - Fast Python package manager
- **Taskfile** - Task automation
- **Devbox** - Isolated development environment
- **Pytest** - Testing framework
- **Ruff** - Linting and formatting
- **MyPy** - Static type checking

## License

TBD

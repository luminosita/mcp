# AI Agent MCP Server

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
mcp/
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
├── docs/                    # Documentation
└── artifacts/               # SDLC artifacts

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

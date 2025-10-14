# AI Agent MCP Server - Development Environment Setup

This guide walks you through setting up the development environment for the AI Agent MCP Server project.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Setup Script Usage](#setup-script-usage)
- [Manual Setup](#manual-setup)
- [Verification](#verification)
- [Next Steps](#next-steps)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before running the setup script, ensure you have the following installed:

### Required Software

1. **Python 3.11+**
   ```bash
   python --version  # Should be 3.11 or higher
   ```

2. **Podman** (container runtime)
   ```bash
   podman --version
   ```

3. **Git**
   ```bash
   git --version
   ```

4. **NuShell** (required for setup script)
   ```bash
   nu --version  # Should be 0.106.1 or compatible
   ```

### Platform Support

- ✅ macOS 14+ (Intel and Apple Silicon)
- ✅ Linux (Ubuntu 22.04+, Fedora, Arch)
- ✅ Windows WSL2 (Ubuntu distribution)

## Quick Start

**Goal**: Get from "repository cloned" to "environment ready" in under 30 minutes.

```bash
# 1. Clone the repository
git clone <repository-url>
cd mcp

# 2. Run the automated setup script
nu scripts/setup.nu

# 3. Follow the interactive prompts
# The script will:
# - Detect your operating system
# - Validate prerequisites
# - Install Taskfile (if needed)
# - Install uv package manager
# - Create Python virtual environment
# - Install dependencies
# - Configure .env file
# - Install pre-commit hooks
# - Run validation checks
```

That's it! Your environment is ready.

## Setup Script Usage

### Interactive Mode (Recommended)

Interactive mode prompts you for preferences:

```bash
nu scripts/setup.nu
```

You'll be asked:
- **IDE Setup**: Configure VS Code? (Default: Yes)
- **Verbose Output**: Enable detailed logging? (Default: Yes)

### Silent Mode (CI/CD)

Silent mode uses default preferences without prompts:

```bash
nu scripts/setup.nu --silent
```

Perfect for continuous integration environments or automated deployments.

### Setup Script Phases

The setup script executes 8 phases:

1. **OS Detection** - Identifies your platform (macOS/Linux/WSL2)
2. **Prerequisites Validation** - Checks Python 3.11+, Podman, Git
3. **Taskfile Installation** - Installs task runner (if needed)
4. **UV Installation** - Installs uv package manager
5. **Virtual Environment Setup** - Creates `.venv/` with Python 3.11+
6. **Dependency Installation** - Installs packages from pyproject.toml
7. **Configuration Setup** - Creates .env file, installs pre-commit hooks
8. **Environment Validation** - Runs health checks

### Setup Time

- **First-time setup**: 20-25 minutes (typical)
- **Idempotent re-run**: <2 minutes (validation only)

## Manual Setup

If you prefer manual setup or need to troubleshoot individual steps:

### 1. Install Taskfile

**macOS (Homebrew)**:
```bash
brew install go-task
```

**Linux (binary download)**:
```bash
sh -c "$(curl -fsSL https://taskfile.dev/install.sh)"
```

**Verify**:
```bash
task --version
```

### 2. Install UV Package Manager

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Verify**:
```bash
uv --version
```

### 3. Create Virtual Environment

```bash
uv venv .venv --python 3.11
```

### 4. Install Dependencies

```bash
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

### 5. Configure Environment

```bash
# Copy .env.example to .env
cp .env.example .env

# Edit .env with your configuration
# Set file permissions (owner read/write only)
chmod 600 .env
```

### 6. Install Pre-commit Hooks

```bash
.venv/bin/pre-commit install
```

### 7. Verify Installation

```bash
# Check Python version
.venv/bin/python --version

# Test module import
.venv/bin/python -c "import mcp_server; print('OK')"

# Run tests
task test
```

## Verification

After setup completes, verify your environment:

### 1. Activate Virtual Environment

```bash
source .venv/bin/activate
```

### 2. Check Installed Packages

```bash
uv pip list
```

### 3. Run Health Checks

```bash
# Via setup script validation
nu -c "use scripts/lib/validation.nu; validate_environment"

# Via Python
python -c "import mcp_server; print('MCP Server ready!')"
```

### 4. Run Tests

```bash
task test
```

Expected output: All tests pass ✅

## Next Steps

Your development environment is ready! Here's what to do next:

### 1. Start Development Server

```bash
task dev
```

The server will start and listen for connections.

### 2. Explore Available Commands

```bash
task --list
```

Common commands:
- `task dev` - Start development server
- `task test` - Run tests
- `task lint` - Run linters (ruff, mypy)
- `task format` - Format code
- `task build` - Build project
- `task clean` - Clean build artifacts

### 3. Run Tests

```bash
# Run all tests
task test

# Run specific test file
pytest tests/unit/test_example.py

# Run with coverage
task test-coverage
```

### 4. Review Documentation

- **Architecture**: See `docs/ARCHITECTURE.md`
- **Contributing**: See `docs/CONTRIBUTING.md`
- **API Documentation**: See `docs/API.md`

## Troubleshooting

### Common Issues

#### Python Version Too Low

**Error**: "Python 3.11+ required"

**Solution**:
```bash
# Install Python 3.11+ via your package manager
# macOS:
brew install python@3.11

# Ubuntu:
sudo apt install python3.11

# Then re-run setup
nu scripts/setup.nu
```

#### UV Installation Fails

**Error**: "UV installation failed after 3 attempts"

**Solution**:
```bash
# Try manual installation
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH
export PATH="$HOME/.cargo/bin:$PATH"

# Verify
uv --version
```

#### Dependency Installation Fails

**Error**: "Dependency installation failed"

**Solution**:
```bash
# Check network connectivity
ping pypi.org

# Try installing with verbose output
uv pip install -e . -v

# Check pyproject.toml syntax
cat pyproject.toml
```

#### Taskfile Installation Fails

**Error**: "Taskfile installation failed"

**Solution**:
```bash
# The setup continues in degraded mode
# Install Taskfile manually:

# macOS:
brew install go-task

# Linux:
sh -c "$(curl -fsSL https://taskfile.dev/install.sh)"

# Verify
task --version
```

#### Pre-commit Hooks Fail

**Error**: "Pre-commit hooks installation failed"

**Solution**:
```bash
# Ensure pre-commit is installed
.venv/bin/pip install pre-commit

# Install hooks
.venv/bin/pre-commit install

# Test hooks
.venv/bin/pre-commit run --all-files
```

### Platform-Specific Issues

#### macOS: Command Line Tools Required

**Error**: "xcrun: error: invalid active developer path"

**Solution**:
```bash
xcode-select --install
```

#### Linux: Permission Denied

**Error**: "Permission denied" when installing Taskfile

**Solution**:
```bash
# Install to user directory (no sudo needed)
sh -c "$(curl -fsSL https://taskfile.dev/install.sh)" -- -b ~/.local/bin
```

#### WSL2: Network Issues

**Error**: "Network timeout" during downloads

**Solution**:
```bash
# Check WSL networking
ping google.com

# Reset WSL network (Windows PowerShell as Admin)
wsl --shutdown
# Then restart WSL
```

### Get Help

For additional help:

1. **Check Troubleshooting Guide**: See `docs/TROUBLESHOOTING.md`
2. **Review Setup Logs**: Logs are in `logs/setup.log`
3. **Run Validation**: `nu -c "use scripts/lib/validation.nu; validate_environment"`
4. **File an Issue**: [GitHub Issues](https://github.com/your-org/mcp-server/issues)

## Advanced Configuration

### Custom Python Version

```bash
# Use specific Python version
nu scripts/setup.nu
# When prompted, the script uses Python 3.11 by default
# To override, edit scripts/setup.nu line 105
```

### Skip IDE Setup

```bash
# Run in silent mode (skips IDE setup)
nu scripts/setup.nu --silent

# Or answer "No" to IDE prompt in interactive mode
```

### Parallel Setup (Multiple Developers)

The setup script is idempotent and safe to run multiple times. Each developer can run it independently without conflicts.

### Container-Based Development

```bash
# Build development container
task container-build

# Run in container
task container-dev
```

---

**Setup Complete!** 🎉

You're ready to start developing on the AI Agent MCP Server project.

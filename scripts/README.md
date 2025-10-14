# Scripts Directory

This directory contains NuShell setup scripts and automation for the AI Agent MCP Server project.

## Directory Structure

```
scripts/
├── setup.nu              # Main setup orchestrator (entry point)
├── lib/                  # NuShell module library
│   ├── os_detection.nu          # OS detection module
│   ├── prerequisites.nu         # Prerequisites validation
│   ├── taskfile_install.nu      # Taskfile installation
│   ├── uv_install.nu            # UV package manager installation
│   ├── venv_setup.nu            # Virtual environment setup
│   ├── deps_install.nu          # Dependency installation
│   ├── config_setup.nu          # Configuration setup
│   ├── validation.nu            # Environment validation
│   ├── interactive.nu           # Interactive prompts
│   └── error_handler.nu         # Error handling and retry logic
└── tests/                # NuShell module tests
    ├── test_os_detection.nu
    ├── test_prerequisites.nu
    └── test_taskfile_install.nu
```

## Usage

### Running Setup Script

```bash
# Enter devbox shell
devbox shell

# Run setup script
nu scripts/setup.nu

# Run in silent mode (CI/automation)
nu scripts/setup.nu --silent
```

### Running Tests

```bash
# Run individual test file
nu scripts/tests/test_os_detection.nu
nu scripts/tests/test_prerequisites.nu
nu scripts/tests/test_taskfile_install.nu

# Or run all tests
for test in (ls scripts/tests/test_*.nu) {
    nu $test.name
}
```

## Module Conventions

### Import Pattern (per SPEC-001 D1)

All modules use **explicit exports** with `export def`:

```nushell
# In module file (scripts/lib/my_module.nu)
export def my_function [] -> string {
    "Hello from module"
}

# In another file
use scripts/lib/my_module.nu my_function
let result = (my_function)
```

### From Test Files

Tests import modules using relative paths:

```nushell
# In scripts/tests/test_my_module.nu
use ../lib/my_module.nu my_function
```

## Module Documentation

### os_detection.nu

Detects operating system, architecture, and version.

**Exported Functions:**
- `detect_os [] -> record<os: string, arch: string, version: string>`

**Supported OS:**
- macOS (Darwin)
- Linux (Ubuntu, Fedora, Arch, etc.)
- WSL2 (Windows Subsystem for Linux)

### prerequisites.nu

Validates required tools are installed and meet version requirements.

**Exported Functions:**
- `check_prerequisites [] -> record`

**Validated Tools:**
- Python 3.11+
- Podman
- Git

### taskfile_install.nu

Handles cross-platform Taskfile installation with retry logic.

**Exported Functions:**
- `ensure_taskfile [os_info: record] -> record`

**Installation Methods:**
- macOS: Homebrew (preferred) + binary fallback
- Linux: Binary download with checksum verification
- WSL2: apt (if available) + binary fallback

**Features:**
- Retry logic (3 attempts, exponential backoff)
- Checksum verification for security
- Graceful degradation on failure

## Development Guidelines

### Adding New Modules

1. Create module file in `scripts/lib/module_name.nu`
2. Use explicit exports: `export def function_name [] { ... }`
3. Add module header documentation with usage examples
4. Create test file in `scripts/tests/test_module_name.nu`
5. Import with relative path: `use ../lib/module_name.nu function_name`

### Testing Requirements

- All modules must have corresponding test files
- Tests must use explicit import pattern
- Tests should be idempotent (can run multiple times)
- Tests should work in any environment (use mocks when needed)

### Code Style

- Use structured data (records, lists) over string parsing
- Prefer NuShell built-in commands over external tools
- Use `try-catch` for error handling
- Provide actionable error messages with remediation steps
- Document function parameters and return types

## Related Documentation

- **CLAUDE.md** - Root orchestration and conventions (Section: Implementation Phase Instructions)
- **SPEC-001** - Technical specification for setup script
- **US-001** - User story for automated setup script
- **devbox.json** - Development environment configuration

# CLAUDE.md - Core Python Development Guide

> **Hybrid Approach**: This is the lean core configuration. For detailed examples and specialized guidance, see the specialized configuration files linked below.
>
> **Taskfile Interface**: Use `task <command>` for all development operations. Taskfile provides a unified CLI interface across all projects, abstracting underlying tools (uv, ruff, mypy, pytest) for consistency.

## 📚 Specialized Configuration Files

### Development Tools & Practices
- **[patterns-tooling]mcp://resources/patterns/python/patterns-tooling** - Development tools: Taskfile, UV, Ruff, MyPy, pytest, Renovate, NuShell, Devbox, Podman, Trivy container security scanning
- **[patterns-testing]mcp://resources/patterns/python/patterns-testing** - Testing strategy, fixtures, and coverage requirements
- **[patterns-typing]mcp://resources/patterns/python/patterns-typing** - Type hints, annotations, and type safety patterns
- **[patterns-mcp]mcp://resources/patterns/python/patterns-mcp** - Model Context Protocol (MCP) tool implementation patterns with FastMCP

### Architecture & Design
- **[patterns-architecture-structure]mcp://resources/patterns/python/patterns-architecture-structure** - Project structure, folder organization, and layout strategies
- **[patterns-architecture-patterns]mcp://resources/patterns/python/patterns-architecture-patterns** - Design patterns, dependency injection, and FastAPI structure
- **[patterns-architecture-middleware]mcp://resources/patterns/python/patterns-architecture-middleware** - Exception handling and CORS configuration
- **[patterns-architecture-data]mcp://resources/patterns/python/patterns-architecture-data** - Database transactions, isolation levels, and models
- **[patterns-architecture-observability]mcp://resources/patterns/python/patterns-architecture-observability** - Structured logging and caching strategies

### Validation & Security
- **[patterns-validation-models]mcp://resources/patterns/python/patterns-validation-models** - Pydantic models, field validation, and CRUD patterns
- **[patterns-validation-security]mcp://resources/patterns/python/patterns-validation-security** - Input sanitization, SQL injection prevention, and path traversal protection
- **[patterns-validation-auth]mcp://resources/patterns/python/patterns-validation-auth** - JWT authentication, token validation, and authorization
- **[patterns-validation-files]mcp://resources/patterns/python/patterns-validation-files** - Secure file upload handling and storage
- **[patterns-validation-api]mcp://resources/patterns/python/patterns-validation-api** - API rate limiting, validation patterns, and security checklists

---

## 🎯 Core Development Philosophy

### KISS (Keep It Simple, Stupid)
Simplicity is a key design goal. Choose straightforward solutions over complex ones. Simple solutions are easier to understand, maintain, and debug.

### YAGNI (You Aren't Gonna Need It)
Implement features only when needed, not when anticipated for future use. Avoid speculative development.

### The Zen of Python (PEP 20)
Follow Python's guiding principles:
- Beautiful is better than ugly
- Explicit is better than implicit
- Simple is better than complex
- Readability counts
- Errors should never pass silently

### SOLID Principles
- **Single Responsibility**: Each class, function, and module has one clear purpose
- **Open/Closed Principle**: Open for extension, closed for modification
- **Liskov Substitution**: Objects replaceable with instances of their subtypes
- **Interface Segregation**: No forced dependencies on unused interfaces
- **Dependency Inversion**: Depend on abstractions, not concretions

---

## 🧱 Code Structure & Modularity

### File and Function Limits
- **Files**: Maximum 500 lines - refactor by extracting modules if approaching this limit
- **Functions**: Maximum 50 lines for better AI comprehension and maintainability
- **Classes**: Focus on single responsibility
- **Cyclomatic complexity**: Maximum 10 per function

### Project Structure (src Layout)
```
project-root/
├── pyproject.toml          # Configuration and dependencies
├── uv.lock                 # Locked dependencies
├── CLAUDE.md               # This file
├── src/
│   └── mcp_server/       # Source code
│       ├── __init__.py
│       ├── main.py
│       ├── core/           # Core business logic
│       ├── models/         # Data models
│       ├── services/       # Business services
│       ├── utils/          # Utilities
│       └── api/            # API endpoints
└── tests/                  # Tests (unit, integration, e2e)
    ├── conftest.py
    ├── unit/
    └── integration/
```

**See [patterns-architecture-structure]mcp://resources/patterns/python/patterns-architecture-structure for detailed structure patterns**

---

## 📋 Code Style & Conventions

### Python Style Guide (PEP 8)
- **Line length**: 88-100 characters (configured in Ruff)
- **Indentation**: 4 spaces (no tabs)
- **Quotes**: Double quotes for strings
- **Imports**: Group by standard library, third-party, local

### Naming Conventions
- **Modules**: `lowercase_with_underscores`
- **Classes**: `PascalCase` (e.g., `UserService`)
- **Functions/Variables**: `snake_case` (e.g., `get_user_by_id`)
- **Constants**: `UPPER_SNAKE_CASE`
- **Private**: Leading underscore `_private`
- **Type Variables**: `T`, `K`, `V` or descriptive `UserT`

---

## 🎯 Type Safety & Annotations

### Type Hints Are Mandatory
- Always use type hints for function signatures
- Use modern syntax: `list[str]` instead of `typing.List[str]` (Python 3.9+)
- Use Union types: `str | int` instead of `typing.Union[str, int]` (Python 3.10+)
- Annotate return types including `None`
- No `Any` type unless absolutely necessary

```python
from typing import Optional
from collections.abc import Sequence, Mapping

def process_items(items: list[str]) -> dict[str, int]:
    """Process items and return counts."""
    return {item: len(item) for item in items}
```

**See [patterns-typing]mcp://resources/patterns/python/patterns-typing for comprehensive type annotation patterns**

---

## 📖 Documentation Standards

### Docstring Requirements (Google Style)
Every public class, function, and method MUST have docstrings:

```python
def calculate_discount(
    original_price: float,
    discount_percent: float,
    min_price: float = 0.0,
) -> float:
    """Calculate the discount price for a product.

    Args:
        original_price: The original price of the product.
        discount_percent: The discount percentage (0-100).
        min_price: The minimum allowed price after discount.

    Returns:
        The calculated discount price.

    Raises:
        ValueError: If parameters are invalid.

    Example:
        >>> calculate_discount(100.0, 20.0, 10.0)
        80.0
    """
```

---

## 🧪 Testing Strategy

### Test Requirements
- Unit tests: Mirror source structure in `tests/unit/`
- Integration tests: Separate `tests/integration/` folder
- Test naming: `test_should_expected_behavior_when_condition`
- Minimum 80-85% coverage
- All public functions/methods must have tests

### Basic Test Structure
```python
import pytest

@pytest.fixture
def sample_user() -> dict[str, str | int]:
    """Provide sample user data for tests."""
    return {"id": 1, "name": "John Doe", "email": "john@example.com"}

def test_should_return_user_when_valid_id_provided(sample_user):
    """Test user retrieval with valid ID."""
    # Arrange, Act, Assert
    pass
```

**See [patterns-testing]mcp://resources/patterns/python/patterns-testing for comprehensive testing patterns**

---

## 🛠️ Development Tools

### Taskfile (Primary Interface)
```bash
# Essential commands - use Taskfile for ALL operations
task --list                # Show all available tasks
task setup                 # Initial project setup
task check                 # Run all quality checks
```

### Dependency Management (via Taskfile)
```bash
task deps:install          # Install dependencies
task deps:add -- PKG=requests          # Add dependency
task deps:add:dev -- PKG=pytest        # Add dev dependency
task deps:update           # Update dependencies
```

### Code Quality (via Taskfile)
```bash
# Linting and formatting
task lint:fix              # Check and fix issues
task format                # Format code
task lint:all              # Lint + format

# Type checking
task type-check            # Type check with strict mode

# Testing
task test                  # Run tests with coverage
task test:coverage         # Run tests with 80%+ enforcement
```

**See [patterns-tooling]mcp://resources/patterns/python/patterns-tooling for comprehensive Taskfile commands and tool configuration**

---

## 🔐 Input Validation & Security

### Pydantic for Validation
All input validation uses Pydantic models:

```python
from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    """User creation model with validation."""
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(ge=13, le=120)
```

### Security Best Practices
- Never commit secrets - use environment variables
- Validate all user input with Pydantic
- Use parameterized queries for database operations
- Keep dependencies updated with `uv`
- Follow OWASP guidelines

**See [patterns-validation-models]mcp://resources/patterns/python/patterns-validation-models for comprehensive validation patterns**

---

## 🔄 Git Workflow

### Commit Message Format
**Never include "claude code" or "written by claude code" in commit messages**

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types: feat, fix, docs, style, refactor, test, chore

Example:
```
feat(auth): add JWT token validation

- Implement JWT token validation middleware
- Add token refresh endpoint
- Update user authentication flow

Closes #156
```

---

## 🔍 Search Command Requirements

**CRITICAL**: Always use `rg` (ripgrep) instead of traditional `grep` and `find` commands:

```bash
# ✅ Use rg instead of grep
rg "pattern"

# ✅ Use rg with file filtering
rg --files -g "*.py"
```

---

## ⚠️ Critical Guidelines

1. **Always use type hints** - Complete function signatures required
2. **No `Any` type** - Use specific types or protocols
3. **Validate all inputs** - Use Pydantic models
4. **Document all public APIs** - Complete docstrings mandatory
5. **Test everything** - Minimum 80% coverage
6. **Handle all exceptions** - No bare except blocks
7. **Use modern Python syntax** - Target Python 3.9+ features
8. **No magic numbers** - Extract to named constants
9. **Follow Ruff rules** - Zero errors in CI
10. **Secure by default** - No hardcoded secrets

---

## 📋 Pre-commit Checklist

Run `task check` to verify all requirements:

- [ ] All type hints added (`task type-check` passes)
- [ ] Docstrings for all public functions/classes
- [ ] Tests written 80%+ coverage (`task test:coverage` passes)
- [ ] Linting and formatting pass (`task lint:all` passes)
- [ ] No security issues
- [ ] Dependencies locked (uv.lock updated via `task deps:*`)
- [ ] Documentation updated if needed

**Quick command**: `task check` runs all quality checks

---

## 🚀 Quick Reference

### Development Setup
```bash
task setup                 # Install dependencies and setup hooks
task info                  # Show environment information
```

### Quality Checks
```bash
task check                 # Run all checks (lint, format, type, test)
task lint:fix              # Fix linting issues
task format                # Format code
task type-check            # Type check with strict mode
task test:coverage         # Run tests with coverage enforcement
```

### Development Workflow
```bash
task dev                   # Start development server
task test:watch            # Run tests in watch mode
task db:start              # Start database
task container:build       # Build container image
```

### Show All Commands
```bash
task --list                # List all available tasks
```

---

**For detailed examples, patterns, and advanced configurations, refer to the specialized CLAUDE-*.md files organized by category at the top of this document.**

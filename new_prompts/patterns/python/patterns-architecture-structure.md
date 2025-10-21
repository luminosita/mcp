# patterns-architecture-structure - Project Structure & Layouts

> **Specialized Guide**: Project structure patterns, folder organization, and layout strategies for Python projects.

## 🏗️ Project Structure Philosophy

### Src Layout Benefits
- **Better test isolation** - Tests can't accidentally import from source
- **Cleaner imports** - Explicit package structure
- **Editable installs** - Proper development workflow
- **Distribution ready** - Build and publish easily

### Vertical Slice Architecture
- **Feature-based organization** - Group by feature, not layer
- **Tests live with code** - Easy to find and maintain
- **Clear boundaries** - Self-contained modules
- **Reduced coupling** - Features are independent

---

## 📁 Standard Project Structure

### Basic Layout

```
project-root/
├── pyproject.toml              # Project metadata and dependencies
├── uv.lock                     # Locked dependencies
├── README.md                   # Project documentation
├── LICENSE                     # License file
├── .gitignore                  # Git ignore rules
├── .env.example                # Example environment variables
│
├── .claude/                    # Claude Code configuration
│   └── commands/               # Custom commands
│
├── src/                        # Source code
│   └── mcp_server/
│       ├── __init__.py
│       ├── __main__.py         # Entry point for -m execution
│       ├── main.py             # Application entry
│       │
│       ├── core/               # Core business logic
│       │   ├── __init__.py
│       │   ├── models.py
│       │   ├── exceptions.py
│       │   └── constants.py
│       │
│       ├── models/             # Data models
│       │   ├── __init__.py
│       │   ├── user.py
│       │   └── product.py
│       │
│       ├── services/           # Business services
│       │   ├── __init__.py
│       │   ├── user_service.py
│       │   └── auth_service.py
│       │
│       ├── repositories/       # Data access layer
│       │   ├── __init__.py
│       │   ├── base.py
│       │   └── user_repository.py
│       │
│       ├── api/                # API endpoints
│       │   ├── __init__.py
│       │   ├── routes/
│       │   │   ├── users.py
│       │   │   └── products.py
│       │   └── schemas/
│       │       ├── user.py
│       │       └── product.py
│       │
│       ├── utils/              # Utility functions
│       │   ├── __init__.py
│       │   ├── helpers.py
│       │   └── validators.py
│       │
│       └── config/             # Configuration
│           ├── __init__.py
│           └── settings.py
│
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── conftest.py             # Shared fixtures
│   │
│   ├── unit/                   # Unit tests
│   │   ├── test_models.py
│   │   ├── test_services.py
│   │   └── test_utils.py
│   │
│   ├── integration/            # Integration tests
│   │   ├── test_database.py
│   │   └── test_api.py
│   │
│   └── e2e/                    # End-to-end tests
│       └── test_workflows.py
│
├── docs/                       # Documentation
│   ├── api.md
│   ├── architecture.md
│   └── deployment.md
│
└── scripts/                    # Development scripts (NuShell)
    ├── setup.nu                # Main setup script (orchestrator)
    ├── lib/                    # NuShell modules (use explicit exports)
    └── tests/                  # Script test suite
        └── integration         # Integration script test suite
```

---

## 🎯 Alternative: Vertical Slice Structure

### Feature-Based Organization

```
project-root/
├── src/
│   └── mcp_server/
│       ├── __init__.py
│       ├── main.py
│       │
│       ├── shared/             # Shared components
│       │   ├── __init__.py
│       │   ├── database.py
│       │   ├── exceptions.py
│       │   └── middleware.py
│       │
│       ├── features/           # Feature slices
│       │   │
│       │   ├── users/          # User management feature
│       │   │   ├── __init__.py
│       │   │   ├── models.py
│       │   │   ├── service.py
│       │   │   ├── repository.py
│       │   │   ├── routes.py
│       │   │   ├── schemas.py
│       │   │   └── tests/
│       │   │       ├── test_service.py
│       │   │       └── test_routes.py
│       │   │
│       │   ├── products/       # Product management feature
│       │   │   ├── __init__.py
│       │   │   ├── models.py
│       │   │   ├── service.py
│       │   │   ├── repository.py
│       │   │   ├── routes.py
│       │   │   ├── schemas.py
│       │   │   └── tests/
│       │   │       ├── test_service.py
│       │   │       └── test_routes.py
│       │   │
│       │   └── orders/         # Order processing feature
│       │       ├── __init__.py
│       │       ├── models.py
│       │       ├── service.py
│       │       ├── repository.py
│       │       ├── routes.py
│       │       ├── schemas.py
│       │       └── tests/
│       │           ├── test_service.py
│       │           └── test_routes.py
│       │
│       └── config/
│           └── settings.py
```

---

## 📋 Structure Selection Guide

### When to Use Standard Layout
- **Small to medium projects** - Clear separation of concerns
- **Team familiar with layered architecture** - Traditional approach
- **Multiple features sharing common patterns** - Centralized services/repositories
- **Learning projects** - Easier to understand for beginners

### When to Use Vertical Slice
- **Large projects** - Better scalability and isolation
- **Microservices mindset** - Feature independence
- **Multiple teams** - Clear ownership boundaries
- **Evolving requirements** - Easy to add/remove features

---

## ⚠️ Structure Best Practices

✅ **DO:**
- Keep modules focused on single responsibility
- Use `__init__.py` for clean public APIs
- Mirror test structure with source layout
- Use relative imports within packages
- Document folder purposes in README

❌ **DON'T:**
- Create deeply nested folder structures (max 3-4 levels)
- Mix different concerns in same module
- Import from implementation details (use `__init__.py`)
- Use circular imports between modules
- Create "utils" dumping ground (be specific)

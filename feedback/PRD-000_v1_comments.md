## Context - Hybrid CLAUDE.md approach

### CLAUDE.md - Core Python Development Guide

> **Hybrid Approach**: This is the lean core configuration. For detailed examples and specialized guidance, see the specialized configuration files linked below.

Main implementation-aware CLAUDE.md is @implementation/CLAUDE-core.md

### 📚 Specialized Configuration Files
- **[CLAUDE-tooling.md](@implementation/CLAUDE-tooling.md)** - UV, Ruff, MyPy, pytest configuration and commands
- **[CLAUDE-testing.md](@implementation/CLAUDE-testing.md)** - Testing strategy, fixtures, and coverage requirements
- **[CLAUDE-typing.md](@implementation/CLAUDE-typing.md)** - Type hints, annotations, and type safety patterns
- **[CLAUDE-validation.md](@implementation/CLAUDE-validation.md)** - Pydantic models, input validation, and security
- **[CLAUDE-architecture.md](@implementation/CLAUDE-architecture.md)** - Project structure, modularity, and design patterns

## Technical Considerations - PRD Section Instructions

- Evaluate alignment of entire Technical Consideration section with already establish standard defined in "Hybrid CLAUDE.md approach". Each specialized CLAUDE.md reflects upon facts presented in Technical Considerations and the first goal is to align those facts.

## Additional PRD Requirements

- Renovate tool (https://github.com/renovatebot/renovate, Cross-platform Dependency Automation) - to keep library versions up-to-date
- NuShell (https://www.nushell.sh, cross-platform shell, works on Linux, macOS, BSD, and Windows) - replacement for Bash
- Devbox (https://www.jetify.com/devbox, Portable, Isolated Dev Environments on any Machine) - to provide isolation from local developer's machine and heavily reduce "Work's on my machine" issues 
- Podman (instead of Docker)

## Open Questions - Answers

### Business Questions

1. Comprehensive foundation
2. Platform standards:
    - CI/CD platform: GitHub
    - container registry: DockerHub
    - deployment tooling: Podman, Kubernetes Manifests (ask further questions if my answer did not clarify)
    - secret management: HashiCorp Vault

3. experienced team productivity (more automation, advanced tooling)

### Product/Technical Trade-off Questions (PM + Tech Lead Discussion)

4. uv

5. defer to EPIC-005, minimum viable is Dockerfile + Podman instructions

6. defer to EPIC-004

7. Podman alternative only



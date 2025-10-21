# Context Engineering Framework - Root Orchestration

## General

**Product Name:** AI_Agent_MCP_Server
**Documentation Product Name:** AI Agent MCP Server
**Package Name:** mcp_server (alias: ai_agent_mcp_server)

---

## SDLC Framework Content

**All SDLC framework content is centralized in MCP Server resources:**

📘 **See:** `mcp://resources/sdlc/core` (provided by MCP Server)

**Framework content includes:**
- Framework Design Principles (Template vs Generator Responsibility)
- Decision Hierarchy for Technical Guidance (3-Tier Precedence System)
- Folder Structure (directory hierarchy, file naming conventions)
- Artifact Path Resolution Algorithm (variable substitution, glob strategies)
- SDLC Artifact Dependency Flow (Epic → PRD → FuncSpec → US → Tech Spec → Task)
- Input Classification System (MANDATORY, RECOMMENDED, CONDITIONAL)
- Spike Workflow (time-boxed technical investigations)
- Open Questions Marker System (standardized markers with required sub-fields)
- Placeholder ID Conventions (AAA/BBB/CCC sequence for sub-artifacts)
- ID Assignment Strategy (global sequential numbering)
- Strategic SDLC Decisions (HLS Consolidation decision)

**Local file reference:** `/new_prompts/CLAUDE/sdlc-core.md`

**Note:** During MCP Server migration (US-030), this reference will be replaced with actual MCP resource loading. For now, refer to the local file at `/new_prompts/CLAUDE/sdlc-core.md`.

---

## Generate Command Instructions

### Start New Context (if required)
- Most tasks require fresh Claude Code session
- Check task `Context:` field in TODO.md
- If "New session CX required", start clean session

## Instructions for TODO.md Tasks
Upon completion, update relevant task status in `/TODO.md`:
- Mark current task checkbox as complete
- Update task status notes
- Add entry to task completion log if applicable

## Commands Reference

### Primary Commands
- `/generate TASK-XXX` - Execute a generator from TODO.md
- `/refine {name}_generator` - Iterate based on feedback

---

## Implementation Phase Instructions

**When to use Implementation Phase instructions:**
- Writing code, tests, documentation
- Setting up development environment, CI/CD, tooling
- Implementing features from PRDs/Backlog Stories
- Coding tasks after planning phase completes

**Language-Specific Implementation Guides:**

Language-specific CLAUDE.md files are organized by programming language in subdirectories:
- **Python Projects:** `new_prompts/CLAUDE/python/`
- **Go Projects:** `new_prompts/CLAUDE/go/`
- Additional languages added as needed (e.g., `new_prompts/CLAUDE/rust/`, `new_prompts/CLAUDE/java/`)

**Implementation Configuration Files (Language-Specific):**
- **CLAUDE-core.md** - Main implementation guide and orchestration
- **CLAUDE-tooling.md** - Language-specific tooling (build tools, linters, formatters, test runners)
- **CLAUDE-testing.md** - Testing strategy, fixtures, coverage
- **CLAUDE-typing.md** - Type system patterns and type safety
- **CLAUDE-validation.md** - Input validation, data models, security patterns
- **CLAUDE-architecture.md** - Project structure, modularity, design patterns

**→ For implementation work, navigate to the appropriate language subdirectory and see CLAUDE-core.md which orchestrates all specialized configs.**

**Current Project Language:** Python (see `new_prompts/CLAUDE/python/` for implementation guides)

---

**Document Version**: 2.5 (Refactored - Orchestrator Only)
**Last Updated**: 2025-10-21
**Maintained By**: Context Engineering PoC Team
**Next Review**: End of Phase 1

**Version History:**
- v2.5 (2025-10-21): **REFACTORED TO ORCHESTRATOR** - Split CLAUDE.md into lightweight orchestrator (~60 lines) and SDLC resource (new_prompts/CLAUDE/sdlc-core.md ~1100 lines). Local file now references mcp://resources/sdlc/core for all framework content. Reduced from 1377 lines to ~60 lines. Completed US-028: Refactor Main CLAUDE.md into Orchestrator + SDLC Resource.
- v2.4 (2025-10-21): **SDLC Flow Alignment with Decision Hierarchy** - Fixed misalignment between CLAUDE.md SDLC flow and generator input definitions.
- v2.3 (2025-10-20): **Placeholder ID Conventions Standardized** - Added comprehensive "Placeholder ID Conventions" section with STANDARDIZED alphabetic sequence.
- v2.2 (2025-10-20): **HLS Consolidation IMPLEMENTED (Core Generators)** - Completed tasks 1-4 of HLS Consolidation.
- v2.1 (2025-10-20): Added Decision Hierarchy for Technical Guidance section.
- v2.0 (2025-10-20): **MAJOR UPDATE** - Added Framework Design Principles section documenting Template vs Generator responsibility separation.
- v1.9 (2025-10-18): Added comprehensive tracking tables for SPEC, ADR, SPIKE, and TASK artifacts.
- v1.8 (2025-10-18): Allocated US-028 through US-067 for EPIC-006 (MCP Server Integration).
- v1.7 (2025-10-15): Added Artifact Path Resolution Algorithm section.
- v1.6 (2025-10-14): Added ID Assignment Strategy section.
- v1.5 (2025-10-13): Added Input Classification System.
- v1.4 (2025-10-13): Added centralized Artifact Path Patterns section.
- v1.3 (2025-10-12): Standardized artifact IDs, file naming conventions, and status values.
- v1.2 (2025-10-11): Added Spike artifact to framework.
- v1.1 (2025-10-11): Initial comprehensive version.

**Related Documents:**
- `/new_prompts/CLAUDE/sdlc-core.md` - SDLC framework core resource (contains all framework-wide content)
- `/docs/framework_validation_gaps.md` - Known validation gaps and production requirements
- `/docs/sdlc_artifacts_comprehensive_guideline.md` - Section 1.10 covers Metadata Standards and Traceability
- `/docs/generator_validation_spec.md` - Generator validation specification for enforcing standardized marker system
- `/docs/lean/report.md` - SDLC Documentation Optimization Report (Lean Analysis v1.4)

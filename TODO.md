# Master Plan - Context Engineering PoC

**Document Version**: 1.5
**Last Updated**: 2025-10-18

---

## ⚠️ CRITICAL: Context Management Protocol

**🔴 MANDATORY REQUIREMENT: Each TODO task MUST execute with CLEARED context**

**After executing ANY task:**
1. ✅ **Prompt human to clear the context** to clear conversation context

**Why this matters:**
- Prevents context pollution from prior tasks
- Ensures generators receive only documented inputs (not conversation state)
- Maintains deterministic, reproducible artifact generation
- Validates that CLAUDE.md orchestration works standalone

**❌ DO NOT:**
- Execute multiple `/generate` tasks without clearing context between them
- Continue in session with prior artifact generation without `/clear`
- Assume "it should work" without clearing context first

**✅ ALWAYS:**
- Run `/clear` before EVERY task execution
- Verify clear confirmation before proceeding

---

## Current Phase: Planning (EPIC-006)

**Current Status**: Backlog Story Decomposition In Progress
**Last Completed**: TASK-059 (US-028 through US-034 generation from HLS-006, 2025-10-18)
**Next Task**: TASK-060 (Generate US-035 through US-039 from HLS-007)
**Epic Focus**: MCP Server Integration - Migrate local files (CLAUDE.md, artifacts, generators, templates) to MCP Server resources, prompts, and tools
**Parent Initiative**: INIT-001 (AI Agent MCP Infrastructure)
**Note**: 6 HLS stories completed (HLS-006 through HLS-011, all v2). Ready to generate 43 backlog stories (US-028 through US-070) across 6 TODO tasks (TASK-059 through TASK-064)

---

## Planning Backlog

### ⏳ EPIC-006: MCP Server Integration

**Source**: docs/additions/HLS-resources.md
**Parent Initiative**: INIT-001
**IDs Allocated**: EPIC-006, PRD-006, HLS-006 through HLS-011, US-028 through US-070
**Next Available IDs**: US-071 (after backlog story decomposition completes)
**Context**: New session CX required

**Epic Scope**:
- Migrate CLAUDE.md files to MCP Server Resources (hybrid approach)
- Migrate artifacts, generators, templates to MCP Server Resources
- Convert validation/inference instructions to deterministic Python scripts (MCP Tools)
- Implement task tracking tool (replace TODO.md growth issue)
- Implement artifact ID management tool (replace manual ID tracking)
- Update main CLAUDE.md as orchestrator for MCP Server integration

**Generation Tasks**:

- [X] **TASK-050**: Generate EPIC-006
  - Command: `/generate epic-generator`
  - Input: docs/additions/HLS-resources.md (resource document)
  - Parent: INIT-001 v4
  - Output: artifacts/epics/EPIC-006_mcp_server_sdlc_framework_integration_v1.md
  - Status: ✅ Completed (2025-10-16)
  - Validation: 25/25 criteria passed
  - Context: Completed in current session

- [X] **TASK-051**: Generate PRD-006 v1
  - Command: `/generate prd-generator`
  - Input: artifacts/epics/EPIC-006_mcp_server_sdlc_framework_integration_v1.md (parent epic)
  - Parent: EPIC-006 v1
  - Output: artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v1.md
  - Status: ✅ Completed (2025-10-17)
  - Validation: 26/26 criteria passed (100%)
  - Context: Completed in current session
  - Note: Comprehensive PRD with 24 functional requirements, 8 NFR categories, 5 open questions (3 business, 2 technical trade-offs)

- [X] **TASK-052**: Refine PRD-006 v1 → v2
  - Command: Manual refinement based on feedback
  - Input: feedback/PRD-006_v1_comments.md
  - Parent: PRD-006 v1
  - Output: artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v2.md
  - Status: ✅ Completed (2025-10-18)
  - Changes: Merged two microservices into one, generators as MCP prompts, updated User Flow 1, Go files already exist, replaced Open Questions with Decisions Made (D1-D5)
  - Context: Completed in current session

**HLS Decomposition Tasks** (Next Available IDs: HLS-006 through HLS-011):

- [X] **TASK-053**: Generate HLS-006 (MCP Resources Migration)
  - Command: `/generate hls-generator`
  - Input: artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v2.md
  - Parent: PRD-006 v2
  - Output: artifacts/hls/HLS-006_mcp_resources_migration_v2.md
  - Scope: Refactor CLAUDE.md, migrate CLAUDE-*.md files to MCP resources, migrate templates, implement resource caching
  - Coverage: FR-01, FR-02, FR-04, FR-20
  - Status: ✅ Completed (2025-10-18)
  - Context: Completed in current session

- [X] **TASK-054**: Generate HLS-007 (MCP Prompts - Generators Migration)
  - Command: `/generate hls-generator`
  - Input: artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v2.md
  - Parent: PRD-006 v2
  - Output: artifacts/hls/HLS-007_mcp_prompts_generators_migration_v2.md
  - Scope: Migrate artifact generators to MCP prompts, update /generate command integration
  - Coverage: FR-05
  - Status: ✅ Completed (2025-10-18)
  - Context: Completed in current session

- [X] **TASK-055**: Generate HLS-008 (MCP Tools - Validation and Path Resolution)
  - Command: `/generate hls-generator`
  - Input: artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v2.md
  - Parent: PRD-006 v2
  - Output: artifacts/hls/HLS-008_mcp_tools_validation_path_resolution_v2.md
  - Scope: Implement validate_artifact tool, resolve_artifact_path tool, store_artifact tool, validation checklists as JSON resources
  - Coverage: FR-06, FR-07, FR-16, FR-17, FR-22, FR-23
  - Status: ✅ Completed (2025-10-18)
  - Context: Completed in current session

- [X] **TASK-056**: Generate HLS-009 (Task Tracking Microservice)
  - Command: `/generate hls-generator`
  - Input: artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v2.md
  - Parent: PRD-006 v2
  - Output: artifacts/hls/HLS-009_task_tracking_microservice_v2.md
  - Scope: Implement Task Tracking microservice (Go) with REST API, task tracking endpoints, ID management endpoints, PostgreSQL integration
  - Coverage: FR-08, FR-09, FR-10, FR-11, FR-14, FR-15, FR-18, FR-19
  - Status: ✅ Completed (2025-10-18)
  - Context: Completed in current session
  - Note: Single microservice handling both task tracking and ID management

- [X] **TASK-057**: Generate HLS-010 (CLAUDE.md Orchestration Update & Integration Testing)
  - Command: `/generate hls-generator`
  - Input: artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v2.md
  - Parent: PRD-006 v2
  - Output: artifacts/hls/HLS-010_claude_orchestration_integration_testing_v2.md
  - Scope: Update main CLAUDE.md orchestrator, implement backward compatibility mode, end-to-end integration testing
  - Coverage: FR-12, FR-13
  - Status: ✅ Completed (2025-10-18)
  - Context: Completed in current session

- [X] **TASK-058**: Generate HLS-011 (Production Readiness and Pilot)
  - Command: `/generate hls-generator`
  - Input: artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v2.md
  - Parent: PRD-006 v2
  - Output: artifacts/hls/HLS-011_production_readiness_pilot_v2.md
  - Scope: Performance benchmarking, security review, observability dashboard, production deployment guide, 30-day stability period
  - Coverage: FR-03, FR-21, All NFRs
  - Status: ✅ Completed (2025-10-18)
  - Context: Completed in current session
  - Note: Includes 30-day stability period per Decision D1

**Backlog Story Decomposition Tasks** (Next Available IDs: US-028 through US-070):

- [X] **TASK-059**: Generate US-028 through US-034 (HLS-006: MCP Resources Migration)
  - Command: `/generate backlog-story-generator` (7 iterations)
  - Input: artifacts/hls/HLS-006_mcp_resources_migration_v2.md
  - Parent: HLS-006 v2
  - IDs Allocated: US-028, US-029, US-030, US-031, US-032, US-033, US-034
  - Output: artifacts/backlog_stories/US-{028-034}_*.md
  - Scope:
    - US-028: Refactor Main CLAUDE.md into Orchestrator + SDLC Resource (~3 SP)
    - US-029: Rename CLAUDE.md Files to Patterns (~3 SP) [NEW - v2 addition]
    - US-030: Implement MCP Resource Server for CLAUDE.md Files (~8 SP)
    - US-031: Implement MCP Resource Server for Templates (~5 SP)
    - US-032: Implement Resource Caching with TTL (~5 SP)
    - US-033: Resource Loading Performance Optimization (~3 SP)
    - US-034: Unit and Integration Testing for Resource Server (~5 SP)
  - Status: ✅ Completed (2025-10-18)
  - Context: Completed in current session

- [X] **TASK-060**: Generate US-035 through US-039 (HLS-007: MCP Prompts - Generators Migration)
    - Command: `/generate backlog-story-generator` (5 iterations)
  - Input: artifacts/hls/HLS-007_mcp_prompts_generators_migration_v2.md
  - Parent: HLS-007 v2
  - IDs Allocated: US-035, US-036, US-037, US-038, US-039
  - Output: artifacts/backlog_stories/US-{035-039}_*.md
  - Scope:
    - US-035: Expose Generators as MCP Prompts (~8 SP)
    - US-036: Update /generate Command to Call MCP Prompts (~5 SP)
    - US-037: Integration Testing for All Generator Types (~5 SP)
    - US-038: Backward Compatibility Mode Implementation (~3 SP)
    - US-039: Error Handling and User Messaging (~2 SP)
  - Status: ✅ Completed (2025-10-18)
  - Context: Completed in current session. Also applied feedback to US-034 (converted Open Questions to Decisions Made).

- [X] **TASK-061**: Generate US-040 through US-047 (HLS-008: MCP Tools - Validation and Path Resolution)
  - Command: `/generate backlog-story-generator` (8 iterations)
  - Input: artifacts/hls/HLS-008_mcp_tools_validation_path_resolution_v2.md
  - Parent: HLS-008 v2
  - IDs Allocated: US-040, US-041, US-042, US-043, US-044, US-045, US-046, US-047
  - Output: artifacts/backlog_stories/US-{040-047}_*.md
  - Scope:
    - US-040: Implement validate_artifact Tool (~8 SP)
    - US-041: Migrate Validation Checklists to JSON Resources (~3 SP)
    - US-042: Implement resolve_artifact_path Tool (~5 SP)
    - US-043: Implement store_artifact Tool (~5 SP)
    - US-044: Implement add_task Tool (~5 SP) [NEW - v2 addition]
    - US-045: Add Sub-artifact Evaluation Instructions to All Generators (~5 SP) [NEW - v2 addition]
    - US-046: Tool Invocation Logging (~3 SP)
    - US-047: Integration Testing for All Tools (~5 SP)
  - Status: ✅ Completed (2025-10-18)
  - Context: Completed in current session

- [X] **TASK-062**: Generate US-048 through US-055 (HLS-009: Task Tracking Microservice)
  - Command: `/generate backlog-story-generator` (8 iterations)
  - Input: artifacts/hls/HLS-009_task_tracking_microservice_v2.md
  - Parent: HLS-009 v2
  - Parent PRD: PRD-006 v3
  - IDs Allocated: US-048, US-049, US-050, US-051, US-052, US-053, US-054, US-055
  - Output: artifacts/backlog_stories/US-{048-055}_*.md
  - Scope:
    - US-048: Task Tracking Database Schema and Migrations (~5 SP)
    - US-049: ID Registry Database Schema and Migrations (~5 SP)
    - US-050: Task Tracking REST API Implementation (Go) (~8 SP)
    - US-051: ID Management REST API Implementation (Go) (~8 SP)
    - US-052: API Authentication (API Key/JWT) (~5 SP)
    - US-053: MCP Server Integration (Python MCP Tools) (~5 SP)
    - US-054: Multi-Project Stress Testing (~3 SP)
    - US-055: Observability (Health Check, Logging) (~3 SP)
  - Status: ✅ Completed (2025-10-18)
  - Context: Completed in current session
  - Note: Single microservice handling both task tracking and ID management

- [X] **TASK-063**: Generate US-056 through US-062 (HLS-010: CLAUDE.md Orchestration Update & Integration Testing)
  - Command: `/generate backlog-story-generator` (7 iterations)
  - Input: artifacts/hls/HLS-010_claude_orchestration_integration_testing_v2.md
  - Parent: HLS-010 v2
  - Parent PRD: PRD-006 v3
  - IDs Allocated: US-056, US-057, US-058, US-059, US-060, US-061, US-062
  - Output: artifacts/backlog_stories/US-{056-062}_*.md
  - Scope:
    - US-056: Update CLAUDE.md to Orchestrate MCP Resources (~5 SP)
    - US-057: Update CLAUDE.md to Orchestrate MCP Prompts (~3 SP)
    - US-058: Update CLAUDE.md to Orchestrate MCP Tools (~3 SP)
    - US-059: Implement Backward Compatibility Mode (~5 SP)
    - US-060: End-to-End Integration Testing (10 Workflows) (~8 SP)
    - US-061: Token Usage Measurement and Validation (~3 SP)
    - US-062: Regression Testing (Local File Approach) (~5 SP)
  - Status: ✅ Completed (2025-10-18)
  - Context: Completed in current session

- [X] **TASK-064**: Generate US-063 through US-070 (HLS-011: Production Readiness and Pilot)
  - Command: `/generate backlog-story-generator` (8 iterations)
  - Input: artifacts/hls/HLS-011_production_readiness_pilot_v2.md
  - Parent: HLS-011 v2
  - Parent PRD: PRD-006 v3
  - IDs Allocated: US-063, US-064, US-065, US-066, US-067, US-068, US-069, US-070
  - Output: artifacts/backlog_stories/US-{063-070}_*.md
  - Scope:
    - US-063: Performance Benchmarking Suite (~8 SP)
    - US-064: Multi-Project Scalability Testing (~5 SP)
    - US-065: Security Review and Hardening (~8 SP)
    - US-066: Observability Dashboard Deployment (~5 SP)
    - US-067: Artifact Metadata Resources (FR-03, FR-21) (~5 SP)
    - US-068: Documentation (Migration Guide, API Reference, Deployment) (~8 SP)
    - US-069: 30-Day Stability Period Monitoring (~5 SP)
    - US-070: Production Deployment Guide (~3 SP)
  - Status: ✅ Completed (2025-10-18)
  - Context: Completed in current session

---

## Implementation Tasks

### US-030: Implement MCP Resource Server for Implementation Pattern Files

**Note:** US-030 requires task decomposition per SDLC Section 11 (8 SP, security-critical, cross-domain).

- [ ] **TASK-004**: Implement FastAPI resource endpoints with Pydantic validation
  - Story: US-030
  - Estimated Hours: 4-6 hours
  - Description: FastAPI routes for patterns/{name} and sdlc/core, Pydantic models with path traversal protection, basic error handling
  - Status: ⏳ Pending

- [ ] **TASK-005**: Implement async file loading and error handling
  - Story: US-030
  - Estimated Hours: 3-4 hours
  - Description: Async file I/O with aiofiles, file existence checks, distinguish 404 vs 500 errors
  - Status: ⏳ Pending

- [ ] **TASK-006**: Add structured logging and observability
  - Story: US-030
  - Estimated Hours: 2-3 hours
  - Description: structlog integration, resource access event logging, security event logging (path traversal attempts)
  - Status: ⏳ Pending

- [ ] **TASK-007**: Comprehensive testing for US-030 (unit, integration, security)
  - Story: US-030
  - Estimated Hours: 4-5 hours
  - Description: Unit tests for resource name validation, integration tests for file loading, security tests for path traversal attacks, 80% coverage target
  - Status: ⏳ Pending

### US-035: Expose Generators as MCP Prompts

**Note:** US-035 requires task decomposition per SDLC Section 11 (8 SP, security-critical, performance-critical).

- [ ] **TASK-008**: Implement prompt registration and file scanner module
  - Story: US-035
  - Estimated Hours: 4-6 hours
  - Description: Scan prompts/ directory for *-generator.xml files, map filenames to artifact names (epic-generator.xml → epic), register prompts with FastMCP using @mcp.prompt() decorator
  - Status: ⏳ Pending

- [ ] **TASK-009**: Implement async file loading with security validation
  - Story: US-035
  - Estimated Hours: 4-6 hours
  - Description: Use aiofiles for async I/O to load generator XML content, validate artifact_name parameter to prevent path traversal attacks, implement error handling for missing/malformed files
  - Status: ⏳ Pending

- [ ] **TASK-010**: Implement prompt caching layer with TTL
  - Story: US-035
  - Estimated Hours: 4-6 hours
  - Description: In-memory cache for generator XML content with 5-minute TTL expiration, cache hit/miss metrics, automatic cache invalidation on TTL expiry
  - Status: ⏳ Pending

- [ ] **TASK-011**: Integration testing for all 10 generator prompts
  - Story: US-035
  - Estimated Hours: 4-8 hours
  - Description: Test prompt discovery (list_prompts API), test retrieval for all 10 generators, test caching behavior, test error handling (missing file, malformed XML, path traversal), 80% coverage target
  - Status: ⏳ Pending

---

## Archived Phases

## Phase 1: Backlog Story Generation (HLS-005) - ✅ COMPLETED

## Phase 2: Backlog Story Implementation (HLS-005) - ✅ COMPLETED

---

## Task Status Legend

- ✅ Completed
- ⏳ Pending
- 🔄 In Progress
- ⏸️ Blocked
- ⚠️ Issues Found

---

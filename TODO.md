# Master Plan - Context Engineering PoC

**Document Version**: 1.5
**Last Updated**: 2025-10-18

---

## ⚠️ CRITICAL: Context Management Protocol

**🔴 MANDATORY REQUIREMENT: Each TODO task MUST execute with CLEARED context**

**Before executing ANY task:**
1. ✅ **Run `/clear` command** to clear conversation context
2. ✅ **Verify clean context** (confirmation message displayed)
3. ✅ **Then execute `/generate` command**

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

**Current Status**: Backlog Story Decomposition Ready
**Last Completed**: TASK-058 (HLS-011 generation, 2025-10-18)
**Next Task**: TASK-059 (Generate US-028 through US-033 from HLS-006)
**Epic Focus**: MCP Server Integration - Migrate local files (CLAUDE.md, artifacts, generators, templates) to MCP Server resources, prompts, and tools
**Parent Initiative**: INIT-001 (AI Agent MCP Infrastructure)
**Note**: 6 HLS stories completed (HLS-006 through HLS-011). Ready to generate 40 backlog stories (US-028 through US-067) across 6 TODO tasks (TASK-059 through TASK-064)

---

## Planning Backlog

### ⏳ EPIC-006: MCP Server Integration

**Source**: docs/additions/HLS-resources.md
**Parent Initiative**: INIT-001
**IDs Allocated**: EPIC-006, PRD-006, HLS-006 through HLS-011
**Next Available IDs**: US-028+ (for backlog story decomposition)
**Context**: New session CX required

**Epic Scope**:
- Migrate CLAUDE.md files to MCP Server Resources (hybrid approach)
- Migrate artifacts, generators, templates to MCP Server Resources
- Convert validation/inference instructions to deterministic Python scripts (MCP Tools)
- Implement task tracking tool (replace TODO.md growth issue)
- Implement artifact ID management tool (replace manual ID tracking)
- Update main CLAUDE.md as orchestrator for MCP Server integration

**Generation Tasks**:

- [x] **TASK-050**: Generate EPIC-006
  - Command: `/generate epic-generator`
  - Input: docs/additions/HLS-resources.md (resource document)
  - Parent: INIT-001 v4
  - Output: artifacts/epics/EPIC-006_mcp_server_sdlc_framework_integration_v1.md
  - Status: ✅ Completed (2025-10-16)
  - Validation: 25/25 criteria passed
  - Context: Completed in current session

- [x] **TASK-051**: Generate PRD-006 v1
  - Command: `/generate prd-generator`
  - Input: artifacts/epics/EPIC-006_mcp_server_sdlc_framework_integration_v1.md (parent epic)
  - Parent: EPIC-006 v1
  - Output: artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v1.md
  - Status: ✅ Completed (2025-10-17)
  - Validation: 26/26 criteria passed (100%)
  - Context: Completed in current session
  - Note: Comprehensive PRD with 24 functional requirements, 8 NFR categories, 5 open questions (3 business, 2 technical trade-offs)

- [x] **TASK-052**: Refine PRD-006 v1 → v2
  - Command: Manual refinement based on feedback
  - Input: feedback/PRD-006_v1_comments.md
  - Parent: PRD-006 v1
  - Output: artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v2.md
  - Status: ✅ Completed (2025-10-18)
  - Changes: Merged two microservices into one, generators as MCP prompts, updated User Flow 1, Go files already exist, replaced Open Questions with Decisions Made (D1-D5)
  - Context: Completed in current session

**HLS Decomposition Tasks** (Next Available IDs: HLS-006 through HLS-011):

- [x] **TASK-053**: Generate HLS-006 (MCP Resources Migration)
  - Command: `/generate hls-generator`
  - Input: artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v2.md
  - Parent: PRD-006 v2
  - Output: artifacts/hls/HLS-006_mcp_resources_migration_v1.md
  - Scope: Refactor CLAUDE.md, migrate CLAUDE-*.md files to MCP resources, migrate templates, implement resource caching
  - Coverage: FR-01, FR-02, FR-04, FR-20
  - Status: ✅ Completed (2025-10-18)
  - Context: Completed in current session

- [x] **TASK-054**: Generate HLS-007 (MCP Prompts - Generators Migration)
  - Command: `/generate hls-generator`
  - Input: artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v2.md
  - Parent: PRD-006 v2
  - Output: artifacts/hls/HLS-007_mcp_prompts_generators_migration_v1.md
  - Scope: Migrate artifact generators to MCP prompts, update /generate command integration
  - Coverage: FR-05
  - Status: ✅ Completed (2025-10-18)
  - Context: Completed in current session

- [x] **TASK-055**: Generate HLS-008 (MCP Tools - Validation and Path Resolution)
  - Command: `/generate hls-generator`
  - Input: artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v2.md
  - Parent: PRD-006 v2
  - Output: artifacts/hls/HLS-008_mcp_tools_validation_path_resolution_v1.md
  - Scope: Implement validate_artifact tool, resolve_artifact_path tool, store_artifact tool, validation checklists as JSON resources
  - Coverage: FR-06, FR-07, FR-16, FR-17, FR-22, FR-23
  - Status: ✅ Completed (2025-10-18)
  - Context: Completed in current session

- [x] **TASK-056**: Generate HLS-009 (Task Tracking Microservice)
  - Command: `/generate hls-generator`
  - Input: artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v2.md
  - Parent: PRD-006 v2
  - Output: artifacts/hls/HLS-009_task_tracking_microservice_v1.md
  - Scope: Implement Task Tracking microservice (Go) with REST API, task tracking endpoints, ID management endpoints, PostgreSQL integration
  - Coverage: FR-08, FR-09, FR-10, FR-11, FR-14, FR-15, FR-18, FR-19
  - Status: ✅ Completed (2025-10-18)
  - Context: Completed in current session
  - Note: Single microservice handling both task tracking and ID management

- [x] **TASK-057**: Generate HLS-010 (CLAUDE.md Orchestration Update & Integration Testing)
  - Command: `/generate hls-generator`
  - Input: artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v2.md
  - Parent: PRD-006 v2
  - Output: artifacts/hls/HLS-010_claude_orchestration_integration_testing_v1.md
  - Scope: Update main CLAUDE.md orchestrator, implement backward compatibility mode, end-to-end integration testing
  - Coverage: FR-12, FR-13
  - Status: ✅ Completed (2025-10-18)
  - Context: Completed in current session

- [x] **TASK-058**: Generate HLS-011 (Production Readiness and Pilot)
  - Command: `/generate hls-generator`
  - Input: artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v2.md
  - Parent: PRD-006 v2
  - Output: artifacts/hls/HLS-011_production_readiness_pilot_v1.md
  - Scope: Performance benchmarking, security review, observability dashboard, production deployment guide, 30-day stability period
  - Coverage: FR-03, FR-21, All NFRs
  - Status: ✅ Completed (2025-10-18)
  - Context: Completed in current session
  - Note: Includes 30-day stability period per Decision D1

**Backlog Story Decomposition Tasks** (Next Available IDs: US-028 through US-067):

- [ ] **TASK-059**: Generate US-028 through US-033 (HLS-006: MCP Resources Migration)
  - **🔴 BEFORE STARTING: Run `/clear` command 🔴**
  - Command: `/generate backlog-story-generator` (6 iterations)
  - Input: artifacts/hls/HLS-006_mcp_resources_migration_v1.md
  - Parent: HLS-006 v1
  - IDs Allocated: US-028, US-029, US-030, US-031, US-032, US-033
  - Output: artifacts/backlog_stories/US-{028-033}_*.md
  - Scope:
    - US-028: Refactor Main CLAUDE.md into Orchestrator + SDLC Resource (~5 SP)
    - US-029: Implement MCP Resource Server for CLAUDE.md Files (~8 SP)
    - US-030: Implement MCP Resource Server for Templates (~5 SP)
    - US-031: Implement Resource Caching with TTL (~5 SP)
    - US-032: Resource Loading Performance Optimization (~3 SP)
    - US-033: Unit and Integration Testing for Resource Server (~5 SP)
  - Status: ⏳ Pending

- [ ] **TASK-060**: Generate US-034 through US-038 (HLS-007: MCP Prompts - Generators Migration)
  - **🔴 BEFORE STARTING: Run `/clear` command 🔴**
  - Command: `/generate backlog-story-generator` (5 iterations)
  - Input: artifacts/hls/HLS-007_mcp_prompts_generators_migration_v1.md
  - Parent: HLS-007 v1
  - IDs Allocated: US-034, US-035, US-036, US-037, US-038
  - Output: artifacts/backlog_stories/US-{034-038}_*.md
  - Scope:
    - US-034: Expose Generators as MCP Prompts (~8 SP)
    - US-035: Update /generate Command to Call MCP Prompts (~5 SP)
    - US-036: Integration Testing for All Generator Types (~5 SP)
    - US-037: Backward Compatibility Mode Implementation (~3 SP)
    - US-038: Error Handling and User Messaging (~2 SP)
  - Status: ⏳ Pending

- [ ] **TASK-061**: Generate US-039 through US-044 (HLS-008: MCP Tools - Validation and Path Resolution)
  - **🔴 BEFORE STARTING: Run `/clear` command 🔴**
  - Command: `/generate backlog-story-generator` (6 iterations)
  - Input: artifacts/hls/HLS-008_mcp_tools_validation_path_resolution_v1.md
  - Parent: HLS-008 v1
  - IDs Allocated: US-039, US-040, US-041, US-042, US-043, US-044
  - Output: artifacts/backlog_stories/US-{039-044}_*.md
  - Scope:
    - US-039: Implement validate_artifact Tool (~8 SP)
    - US-040: Migrate Validation Checklists to JSON Resources (~3 SP)
    - US-041: Implement resolve_artifact_path Tool (~5 SP)
    - US-042: Implement store_artifact Tool (~5 SP)
    - US-043: Tool Invocation Logging (~3 SP)
    - US-044: Integration Testing for All Tools (~5 SP)
  - Status: ⏳ Pending

- [ ] **TASK-062**: Generate US-045 through US-052 (HLS-009: Task Tracking Microservice)
  - **🔴 BEFORE STARTING: Run `/clear` command 🔴**
  - Command: `/generate backlog-story-generator` (8 iterations)
  - Input: artifacts/hls/HLS-009_task_tracking_microservice_v1.md
  - Parent: HLS-009 v1
  - IDs Allocated: US-045, US-046, US-047, US-048, US-049, US-050, US-051, US-052
  - Output: artifacts/backlog_stories/US-{045-052}_*.md
  - Scope:
    - US-045: Task Tracking Database Schema and Migrations (~5 SP)
    - US-046: ID Registry Database Schema and Migrations (~5 SP)
    - US-047: Task Tracking REST API Implementation (Go) (~8 SP)
    - US-048: ID Management REST API Implementation (Go) (~8 SP)
    - US-049: API Authentication (API Key/JWT) (~5 SP)
    - US-050: MCP Server Integration (Python MCP Tools) (~5 SP)
    - US-051: Multi-Project Stress Testing (~3 SP)
    - US-052: Observability (Health Check, Logging) (~3 SP)
  - Status: ⏳ Pending
  - Note: Single microservice handling both task tracking and ID management

- [ ] **TASK-063**: Generate US-053 through US-059 (HLS-010: CLAUDE.md Orchestration Update & Integration Testing)
  - **🔴 BEFORE STARTING: Run `/clear` command 🔴**
  - Command: `/generate backlog-story-generator` (7 iterations)
  - Input: artifacts/hls/HLS-010_claude_orchestration_integration_testing_v1.md
  - Parent: HLS-010 v1
  - IDs Allocated: US-053, US-054, US-055, US-056, US-057, US-058, US-059
  - Output: artifacts/backlog_stories/US-{053-059}_*.md
  - Scope:
    - US-053: Update CLAUDE.md to Orchestrate MCP Resources (~5 SP)
    - US-054: Update CLAUDE.md to Orchestrate MCP Prompts (~3 SP)
    - US-055: Update CLAUDE.md to Orchestrate MCP Tools (~3 SP)
    - US-056: Implement Backward Compatibility Mode (~5 SP)
    - US-057: End-to-End Integration Testing (10 Workflows) (~8 SP)
    - US-058: Token Usage Measurement and Validation (~3 SP)
    - US-059: Regression Testing (Local File Approach) (~5 SP)
  - Status: ⏳ Pending

- [ ] **TASK-064**: Generate US-060 through US-067 (HLS-011: Production Readiness and Pilot)
  - **🔴 BEFORE STARTING: Run `/clear` command 🔴**
  - Command: `/generate backlog-story-generator` (8 iterations)
  - Input: artifacts/hls/HLS-011_production_readiness_pilot_v1.md
  - Parent: HLS-011 v1
  - IDs Allocated: US-060, US-061, US-062, US-063, US-064, US-065, US-066, US-067
  - Output: artifacts/backlog_stories/US-{060-067}_*.md
  - Scope:
    - US-060: Performance Benchmarking Suite (~8 SP)
    - US-061: Multi-Project Scalability Testing (~5 SP)
    - US-062: Security Review and Hardening (~8 SP)
    - US-063: Observability Dashboard Deployment (~5 SP)
    - US-064: Artifact Metadata Resources (FR-03, FR-21) (~5 SP)
    - US-065: Documentation (Migration Guide, API Reference, Deployment) (~8 SP)
    - US-066: 30-Day Stability Period Monitoring (~5 SP)
    - US-067: Production Deployment Guide (~3 SP)
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

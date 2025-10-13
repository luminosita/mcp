# Commands Consolidation Evaluation

**Date:** 2025-10-13
**Purpose:** Evaluate `/generate` and `/refine` commands against Issue #1, #2, #3 consolidation changes

---

## Executive Summary

**Verdict:** ⚠️ **MINOR UPDATES RECOMMENDED**

**What's Already Good:**
- ✅ Commands are workflow-focused, not validation-structure-focused
- ✅ Commands already reference CLAUDE.md as orchestration guide
- ✅ Path references are mostly in examples (not hardcoded logic)
- ✅ Commands focus on task execution, not internal generator structure

**What Needs Updates:**
- ⚠️ Update path examples to reference CLAUDE.md patterns
- ⚠️ Update input validation language (required → classification)
- ⚠️ Add guidance on new validation reporting format (with IDs)
- ⚠️ Clarify path resolution approach (CLAUDE.md as source of truth)

---

## Issue-by-Issue Analysis

### Issue #1: Validation Consolidation

#### Current State in Commands

**`/generate` command:**
- Line 62-66: Reports validation status generically:
  ```
  Validation Status:
  ✅ Status set to "Draft" in metadata
  ✅ All template sections present (8/8)
  ⚠️  Readability: Manual check required
  ✅ Traceability: 3 references to product-idea.md
  ```
- No mention of validation checklist structure (IDs, categories)
- No mention of failure reporting format

**`/refine` command:**
- Line 42-44: Critique parsing mentions categories:
  ```
  - **Completeness Issues**: Missing sections, incomplete information
  - **Clarity Issues**: Confusing language, jargon, poor structure
  - **Actionability Issues**: Vague next steps, missing details
  - **Traceability Issues**: Missing references, unclear connections
  ```
- These categories DON'T align with new validation categories: content, traceability, consistency

#### Impact Assessment

**Severity:** 🟡 Medium

**Issues:**
1. Validation report format doesn't show criterion IDs (e.g., "CQ-03: FAILED")
2. Critique categories (Completeness, Clarity, Actionability, Traceability) don't map to validation categories (content, traceability, consistency)
3. No guidance on how to interpret validation failure reports with IDs

**User Experience Impact:**
- Users won't understand validation IDs when generators report them
- Critique feedback won't align with validation checklist structure
- Harder to trace which specific criterion failed

#### Recommended Changes

**`/generate` command - Step 3: Execute Generator**

**BEFORE:**
```
Validation Status:
✅ Status set to "Draft" in metadata
✅ All template sections present (8/8)
⚠️  Readability: Manual check required
✅ Traceability: 3 references to product-idea.md
```

**AFTER:**
```
Validation Status:
✅ CQ-01: Status set to "Draft" in metadata (content quality)
✅ CQ-02: All template sections present (8/8) (content quality)
⚠️  CC-03: Readability: Manual check required (consistency)
✅ TR-01: Traceability: 3 references to product-idea.md (traceability)

Note: Criterion IDs help identify specific validation failures. See validation_checklist in generator XML.
```

**`/refine` command - Step 3: Analyze Critique**

**BEFORE:**
```
Parse critique file for:
- **Completeness Issues**: Missing sections, incomplete information
- **Clarity Issues**: Confusing language, jargon, poor structure
- **Actionability Issues**: Vague next steps, missing details
- **Traceability Issues**: Missing references, unclear connections
- **Severity Ratings**: Critical, Major, Minor
```

**AFTER:**
```
Parse critique file for validation categories:
- **Content Quality (CQ-##)**: Missing sections, incomplete information, unclear explanations
- **Traceability (TR-##)**: Missing references, unclear connections to input artifacts
- **Consistency (CC-##)**: Terminology inconsistencies, formatting issues, readability problems
- **Severity Ratings**: Critical, Major, Minor

Note: Validation criterion IDs (e.g., CQ-03, TR-01) align with generator validation_checklist.
Reference specific IDs in critique to pinpoint failures.
```

---

### Issue #2: Path Consolidation

#### Current State in Commands

**`/generate` command:**
- Line 30: References `/CLAUDE.md` ✅
- Line 32: References `/prompts/{generator_name}_generator.xml` ✅
- Line 33: References `/artifacts/product_vision_v3.md` ⚠️ (old path format)
- Line 60: Example path `/artifacts/product_visions/VIS-001_AI_Agent_MCP_Server_v1.md` ⚠️ (filesystem path)
- Line 72: Example path `/artifacts/product_visions/VIS-001_AI_Agent_MCP_Server_v1.md` ⚠️
- Line 96: Example path `/artifacts/product_visions/VIS-001_AI_Agent_MCP_Server_v1.md` ⚠️

**`/refine` command:**
- Line 23: References `/prompts/{generator_name}-generator.xml` ✅
- Line 24: References `/prompts/templates/{artifact}-template.xml` ✅
- Line 32: References `/feedback/{artifact}_v{N}_critique.md` ✅
- Line 33: Example `/feedback/product_vision_v1_critique.md` ✅
- Line 158: Example `/artifacts/{artifact}_v{N+1}.md` ⚠️ (generic, but filesystem)
- Line 212: Example `/feedback/{artifact}_v{N}_critique.md` ✅

#### Impact Assessment

**Severity:** 🟢 Low

**Issues:**
1. Example paths use filesystem format, not {SDLC_DOCUMENTS_URL} placeholder
2. No explicit guidance to reference CLAUDE.md for path patterns
3. Commands work fine as-is (paths are just examples), but don't educate users on consolidation

**User Experience Impact:**
- Low: Commands work fine
- Users aren't directed to CLAUDE.md for path patterns
- When paths change, commands need updates (but only in examples)

#### Recommended Changes

**`/generate` command - Step 2: Load Context & Validate Inputs**

**ADD after line 33:**
```
**Path Resolution**:
- All artifact paths defined in CLAUDE.md Artifact Path Patterns section
- Use path patterns like: artifacts/product_visions/VIS-{id}_product_vision_v{version}.md
- For links/URLs in artifacts, use {SDLC_DOCUMENTS_URL} placeholder format
```

**`/generate` command - Report Results (line 60)**

**BEFORE:**
```
✅ Terminal Artifact: /artifacts/product_visions/VIS-001_AI_Agent_MCP_Server_v1.md
```

**AFTER:**
```
✅ Terminal Artifact: artifacts/product_visions/VIS-001_product_vision_v1.md
(Path pattern: artifacts/product_visions/VIS-{id}_product_vision_v{version}.md - see CLAUDE.md)
```

**`/refine` command - Step 7: Re-Execute Generator**

**ADD note after line 134:**
```
Note: Artifact paths follow patterns defined in CLAUDE.md Artifact Path Patterns section.
```

---

### Issue #3: Input Classification

#### Current State in Commands

**`/generate` command:**
- Line 38-43: "Validate input artifact status" mentions:
  ```
  - Parse artifact metadata section for Status field
  - Primary input artifacts should have Status = "Approved"
  - Exception: Research phase artifacts (business_research.md, implementation_research.md) are always approved sources
  - Exception: PoC/development mode may proceed with "Draft" status at risk of rework
  ```
- Uses terminology "Primary input artifacts" (not "mandatory")
- No mention of recommended/conditional/mutually_exclusive inputs

**`/refine` command:**
- No direct mention of input artifact classification

#### Impact Assessment

**Severity:** 🟡 Medium

**Issues:**
1. Uses "Primary input artifacts" terminology instead of "mandatory"
2. No guidance on how to handle recommended inputs (warn if missing)
3. No mention of conditional inputs (load only if condition met)
4. No mention of mutually_exclusive inputs (one of N required)

**User Experience Impact:**
- Users won't understand classification system
- No clarity on when warnings vs errors occur for missing inputs
- Quality degradation from missing recommended inputs not explained

#### Recommended Changes

**`/generate` command - Step 2: Load Context & Validate Inputs**

**REPLACE lines 38-43:**

**BEFORE:**
```
**Context Validation**:
- Verify all required files exist
- Check file sizes to ensure <50% context window usage
- **Validate input artifact status (production requirement)**:
  - Parse artifact metadata section for Status field
  - Primary input artifacts should have Status = "Approved"
  - Exception: Research phase artifacts (business_research.md, implementation_research.md) are always approved sources
  - Exception: PoC/development mode may proceed with "Draft" status at risk of rework
- If any file missing: Prompt human with clear error message
```

**AFTER:**
```
**Context Validation**:
- Verify all files exist and check sizes (<50% context window)
- **Input Classification Handling** (see CLAUDE.md Input Classification System):
  - **Mandatory inputs**: Must exist. Generator FAILS if missing. Status must be "Approved" (production).
  - **Recommended inputs**: WARN if missing. Quality reduced by ~20-30% without. Status should be "Approved".
  - **Conditional inputs**: Load only if condition met. No warning if not loaded.
  - **Mutually Exclusive inputs**: Exactly ONE of group required. FAIL if none or multiple provided.
- **Status Validation (Production)**:
  - Mandatory/Recommended inputs should have Status = "Approved"
  - Exception: Research artifacts (business_research.md, implementation_research.md) always approved
  - Exception: PoC/development may proceed with "Draft" status (risk of rework)
```

**ADD new error example:**

```markdown
### Error: Recommended Input Missing

⚠️ WARNING: Recommended input artifact not found
Input: Business Research (artifacts/research/{product_name}_business_research.md)
Classification: RECOMMENDED
Impact: Output quality reduced by ~25% without market context and user personas

Proceed without recommended input? (y/n)
Note: Generated artifact will be based solely on mandatory inputs.
```

---

## Overall Recommendations

### Priority 1: Update Validation Reporting (Issue #1)

**Effort:** 2-3 hours

**Files to Update:**
1. `/generate` command: Update validation report format with IDs and categories
2. `/refine` command: Update critique parsing to align with validation categories

**Benefit:** Users understand validation failures, can write better critiques

---

### Priority 2: Add Input Classification Guidance (Issue #3)

**Effort:** 1-2 hours

**Files to Update:**
1. `/generate` command: Replace "Primary input" with "Mandatory input", add classification handling
2. `/generate` command: Add error examples for recommended/conditional/mutually_exclusive

**Benefit:** Users understand when warnings vs errors occur, quality impact of missing inputs

---

### Priority 3: Update Path Examples (Issue #2)

**Effort:** 30 minutes - 1 hour

**Files to Update:**
1. `/generate` command: Add CLAUDE.md path reference guidance
2. `/generate` command: Update example paths with pattern notation
3. `/refine` command: Add CLAUDE.md path reference note

**Benefit:** Educational, helps users understand path consolidation

---

## Deferred / Not Needed

### Not Needed: Path Resolution Logic

**Rationale:** Commands don't implement path resolution logic. They work with task IDs from TODO.md and rely on generators/templates to handle paths. Path resolution is LLM's responsibility when executing generator.

### Not Needed: Validation Structure Details

**Rationale:** Commands don't validate artifacts directly. Generators do that. Commands just report results.

### Not Needed: Major Command Restructuring

**Rationale:** Commands work well as-is. Only need alignment updates for consolidation changes.

---

## Implementation Plan

### Option 1: Implement All Updates (RECOMMENDED)

**Timeline:** 3-4 hours total

**Order:**
1. Issue #1: Validation reporting (~2 hours)
2. Issue #3: Input classification (~1.5 hours)
3. Issue #2: Path examples (~30 min)

**Outcome:** Commands fully aligned with consolidation

---

### Option 2: Implement Priority 1 + 2 Only

**Timeline:** 3 hours

**Order:**
1. Issue #1: Validation reporting (~2 hours)
2. Issue #3: Input classification (~1.5 hours)
3. Skip Issue #2 path updates (not critical)

**Outcome:** Commands functionally aligned, path examples outdated but not breaking

---

### Option 3: Defer All Updates (NOT RECOMMENDED)

**Rationale:** Commands work fine as-is for PoC

**Risk:** Users won't understand:
- Validation criterion IDs when generators report them
- Classification system (mandatory vs recommended)
- Path consolidation approach

**When to use:** If timeline very constrained and commands are low-priority for PoC

---

## Evaluation By

**Analyst:** System Analysis
**Date:** 2025-10-13
**Status:** Complete

**Next Action:** Review with user, decide on implementation option

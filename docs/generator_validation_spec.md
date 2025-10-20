# Generator Validation Specification

**Purpose:** Define validation rules for generators to enforce standardized marker system in Open Questions sections.

**Version:** 1.0
**Last Updated:** 2025-10-20
**Related:** Lean Analysis Report v1.4 Recommendation 5 - Enforce Standardized Marker System

---

## Overview

All generators that produce artifacts with Open Questions sections MUST implement validation logic to enforce:
1. **Version lifecycle workflow** (v1 → v2+ progression)
2. **Standardized marker usage** with required sub-fields
3. **Prohibition of free-form text** in v2+ artifacts
4. **"Decisions Made" section** for answered questions

---

## Validation Rules by Artifact Type

### Epic Generator

**Validation Trigger:** After generating v2+ artifacts (when version >= 2)

**Required Checks:**

1. **Section Structure:**
   - [ ] "Decisions Made" section exists (for v2+ only)
   - [ ] "Open Questions" section exists
   - [ ] No other question-related sections present

2. **Decisions Made Section (v2+):**
   - [ ] All entries follow format:
     ```markdown
     **Q[N]: [Question]**
     - **Decision:** [Answer]
     - **Rationale:** [Why this decision was made]
     - **Decided By:** [Person/Role] ([Date])
     ```

3. **Open Questions Section (v2+):**
   - [ ] Each question uses one of the standardized markers:
     - `[REQUIRES EXECUTIVE DECISION]`
     - `[REQUIRES PORTFOLIO PLANNING]`
     - `[REQUIRES RESOURCE PLANNING]`
     - `[REQUIRES ORGANIZATIONAL ALIGNMENT]`
   - [ ] No free-form text patterns:
     - ❌ "Decision: X needed"
     - ❌ "Action Required: Do Y"
   - [ ] Each marker includes ALL required sub-fields

4. **Required Sub-fields by Marker:**

   **[REQUIRES EXECUTIVE DECISION]:**
   - [ ] `**Decision Needed:**` present
   - [ ] `**Options Considered:**` present
   - [ ] `**Business Impact:**` present
   - [ ] `**Decision Deadline:**` present

   **[REQUIRES PORTFOLIO PLANNING]:**
   - [ ] `**Impact:**` present
   - [ ] `**Timeline Dependencies:**` present
   - [ ] `**Resource Impact:**` present

   **[REQUIRES RESOURCE PLANNING]:**
   - [ ] `**Resource Type:**` present
   - [ ] `**Quantity Needed:**` present
   - [ ] `**Duration:**` present
   - [ ] `**Blocking:**` present

   **[REQUIRES ORGANIZATIONAL ALIGNMENT]:**
   - [ ] `**Stakeholders:**` present
   - [ ] `**Alignment Topic:**` present
   - [ ] `**Impact Without Alignment:**` present
   - [ ] `**Decision Deadline:**` present

**Error Messages:**

```
❌ ERROR: Open Question missing standardized marker

Question text: "{question}"
Artifact: EPIC-{XXX} v{N}
Section: Open Questions

Required: Use one of [REQUIRES EXECUTIVE DECISION], [REQUIRES PORTFOLIO PLANNING],
[REQUIRES RESOURCE PLANNING], [REQUIRES ORGANIZATIONAL ALIGNMENT]

Example format:
- What is the acceptable customer acquisition cost for this feature? [REQUIRES EXECUTIVE DECISION]
  - **Decision Needed:** CAC threshold for feature viability
  - **Options Considered:** <$50, <$100, <$200 per customer
  - **Business Impact:** Affects pricing strategy and profit margins
  - **Decision Deadline:** Q1 2025 planning (end of November)
```

```
❌ ERROR: Marker missing required sub-fields

Marker: [REQUIRES EXECUTIVE DECISION]
Question: "{question}"
Artifact: EPIC-{XXX} v{N}

Missing sub-fields:
- **Decision Needed:**
- **Options Considered:**

All required sub-fields for [REQUIRES EXECUTIVE DECISION]:
- Decision Needed, Options Considered, Business Impact, Decision Deadline
```

---

### PRD Generator

**Validation Trigger:** After generating v2+ artifacts (when version >= 2)

**Required Checks:**

1. **Section Structure:**
   - [ ] "Decisions Made" section exists (for v2+ only)
   - [ ] "Open Questions" section exists

2. **Decisions Made Section (v2+):** Same format as Epic

3. **Open Questions Section (v2+):**
   - [ ] Each question uses one of the standardized markers:
     - `[REQUIRES PM + TECH LEAD]`
     - `[REQUIRES EXECUTIVE DECISION]`
     - `[REQUIRES ORGANIZATIONAL ALIGNMENT]`
   - [ ] No free-form text patterns
   - [ ] Each marker includes ALL required sub-fields

4. **Required Sub-fields by Marker:**

   **[REQUIRES PM + TECH LEAD]:**
   - [ ] `**Trade-off:**` present
   - [ ] `**PM Perspective:**` present
   - [ ] `**Tech Perspective:**` present
   - [ ] `**Decision Needed By:**` present

   **[REQUIRES EXECUTIVE DECISION]:** (same as Epic)

   **[REQUIRES ORGANIZATIONAL ALIGNMENT]:** (same as Epic)

**Error Messages:** Similar structure to Epic, adjusted for PRD markers

---

### High-Level Story Generator

**Validation Trigger:** After generating v2+ artifacts (when version >= 2)

**Required Checks:**

1. **Section Structure:**
   - [ ] "Decisions Made" section exists (for v2+ only)
   - [ ] "Open Questions" section exists

2. **Decisions Made Section (v2+):** Same format as Epic

3. **Open Questions Section (v2+):**
   - [ ] Each question uses one of the standardized markers:
     - `[REQUIRES UX RESEARCH]`
     - `[REQUIRES UX DESIGN]`
     - `[REQUIRES PRODUCT OWNER]`
   - [ ] No free-form text patterns
   - [ ] Each marker includes ALL required sub-fields

4. **Required Sub-fields by Marker:**

   **[REQUIRES UX RESEARCH]:**
   - [ ] `**Research Question:**` present
   - [ ] `**Research Method:**` present
   - [ ] `**Timeline:**` present
   - [ ] `**Blocking:**` present

   **[REQUIRES UX DESIGN]:**
   - [ ] `**Design Scope:**` present
   - [ ] `**Design Deliverables:**` present
   - [ ] `**Timeline:**` present
   - [ ] `**Blocking:**` present

   **[REQUIRES PRODUCT OWNER]:**
   - [ ] `**Decision Needed:**` present
   - [ ] `**Context:**` present
   - [ ] `**Impact:**` present

**Error Messages:** Similar structure to Epic, adjusted for HLS markers

---

### Backlog Story Generator

**Validation Trigger:** After generating v2+ artifacts (when version >= 2)

**Required Checks:**

1. **Section Structure:**
   - [ ] "Decisions Made" section exists (for v2+ only)
   - [ ] "Open Questions & Implementation Uncertainties" section exists

2. **Decisions Made Section (v2+):** Same format as Epic

3. **Open Questions Section (v2+):**
   - [ ] Each question uses one of the standardized markers:
     - `[REQUIRES SPIKE]`
     - `[REQUIRES ADR]`
     - `[REQUIRES TECH LEAD]`
     - `[BLOCKED BY]`
   - [ ] No free-form text patterns
   - [ ] Each marker includes ALL required sub-fields

4. **Required Sub-fields by Marker:**

   **[REQUIRES SPIKE]:**
   - [ ] `**Investigation Needed:**` present
   - [ ] `**Spike Scope:**` present
   - [ ] `**Time Box:**` present (must be 1-3 days)
   - [ ] `**Blocking:**` present

   **[REQUIRES ADR]:**
   - [ ] `**Decision Topic:**` present
   - [ ] `**Alternatives:**` present
   - [ ] `**Impact Scope:**` present
   - [ ] `**Decision Deadline:**` present

   **[REQUIRES TECH LEAD]:**
   - [ ] `**Technical Question:**` present
   - [ ] `**Context:**` present
   - [ ] `**Blocking:**` present

   **[BLOCKED BY]:**
   - [ ] `**Dependency:**` present
   - [ ] `**Expected Resolution:**` present
   - [ ] `**Workaround Available:**` present

**Special Validation:**
- [ ] If marker is `[REQUIRES SPIKE]`, Time Box value must be "1 day", "2 days", or "3 days" (hard limit enforcement)

**Error Messages:** Similar structure to Epic, adjusted for US markers

**Example (US-030 v2 Correction):**

```markdown
## Open Questions

- What is the exact MCP protocol error schema structure? [REQUIRES SPIKE]
  - **Investigation Needed:** MCP SDK documentation for expected error response schema
  - **Spike Scope:** Review MCP SDK docs, analyze example error responses, document schema contract
  - **Time Box:** 1 day
  - **Blocking:** Must resolve before implementing error handling
```

---

### Tech Spec Generator

**Validation Trigger:** After generating v2+ artifacts (when version >= 2)

**Required Checks:**

1. **Section Structure:**
   - [ ] "Decisions Made" section exists (for v2+ only)
   - [ ] "Open Questions" section exists

2. **Decisions Made Section (v2+):** Same format as Epic

3. **Open Questions Section (v2+):**
   - [ ] Each question uses one of the standardized markers:
     - `[REQUIRES TECH LEAD]`
     - `[CLARIFY BEFORE START]`
     - `[BLOCKED BY]`
     - `[NEEDS PAIR PROGRAMMING]`
   - [ ] No free-form text patterns
   - [ ] Each marker includes ALL required sub-fields

4. **Required Sub-fields by Marker:**

   **[REQUIRES TECH LEAD]:** (same as US)

   **[CLARIFY BEFORE START]:**
   - [ ] `**Clarification Needed:**` present
   - [ ] `**Stakeholder:**` present
   - [ ] `**Blocking:**` present

   **[BLOCKED BY]:** (same as US)

   **[NEEDS PAIR PROGRAMMING]:**
   - [ ] `**Complexity Area:**` present
   - [ ] `**Skills Needed:**` present
   - [ ] `**Duration:**` present

**Error Messages:** Similar structure to Epic, adjusted for Tech Spec markers

---

### Implementation Task Generator

**Validation Trigger:** After generating v2+ artifacts (when version >= 2)

**Required Checks:**

1. **Section Structure:**
   - [ ] "Decisions Made" section exists (for v2+ only)
   - [ ] "Task-Level Uncertainties & Blockers" section exists

2. **Decisions Made Section (v2+):** Same format as Epic

3. **Task-Level Uncertainties Section (v2+):**
   - [ ] Each uncertainty uses one of the standardized markers:
     - `[CLARIFY BEFORE START]`
     - `[BLOCKED BY]`
     - `[NEEDS PAIR PROGRAMMING]`
     - `[TECH DEBT]`
   - [ ] No free-form text patterns
   - [ ] Each marker includes ALL required sub-fields

4. **Required Sub-fields by Marker:**

   **[CLARIFY BEFORE START]:** (same as Tech Spec)

   **[BLOCKED BY]:** (same as US/Tech Spec)

   **[NEEDS PAIR PROGRAMMING]:** (same as Tech Spec)

   **[TECH DEBT]:**
   - [ ] `**Tech Debt Description:**` present
   - [ ] `**Workaround:**` present
   - [ ] `**Future Resolution:**` present

**Error Messages:** Similar structure to Epic, adjusted for Task markers

---

## Version 1 Artifacts (No Validation)

**For v1 artifacts, generators SHOULD NOT validate marker usage.**

**v1 Open Questions Format (Exploratory):**
```markdown
## Open Questions

- How should error responses be structured to match MCP SDK expectations?
  - **Recommendation:** Review MCP SDK documentation for error response schema patterns
  - **Alternatives:**
    - Option A: Mirror HTTP status code structure (400/500 codes)
    - Option B: Custom error object with code/message/details fields
    - Option C: Follow MCP protocol error conventions
  - **Decision Needed By:** Product Owner + Tech Lead
```

**No markers required in v1.** Generators should allow free-form recommendations.

---

## Meta-Instruction Exception

**Allowed in v2+:**

If a generator detects that markers are missing in a v2+ artifact, it MAY include a meta-instruction:

```markdown
⚠️ **ACTION REQUIRED:** This artifact has 3 open questions without markers.
Add [REQUIRES SPIKE] or [REQUIRES TECH LEAD] markers before finalization. ⚠️
```

**Validation:** This is the ONLY allowed use of "Action Required:" text. It must:
- [ ] Be prefixed with ⚠️ emoji
- [ ] Be in bold: `**ACTION REQUIRED:**`
- [ ] Specify number of questions missing markers
- [ ] Specify which markers to use
- [ ] NOT be used for individual question documentation

---

## Implementation Guidance for Generators

### Step 1: Detect Artifact Version

```python
# Parse artifact metadata
version = extract_version(artifact)  # e.g., "v2"
version_number = int(version.replace('v', ''))  # 2

if version_number == 1:
    # Skip validation for v1 artifacts
    return ValidationResult(valid=True, skip_reason="v1 artifact allows exploratory questions")
```

### Step 2: Parse Open Questions Section

```python
# Extract Open Questions section content
open_questions_section = extract_section(artifact, "Open Questions")

# Extract Decisions Made section (v2+ only)
if version_number >= 2:
    decisions_made_section = extract_section(artifact, "Decisions Made")
    if decisions_made_section is None:
        return ValidationError("Missing 'Decisions Made' section in v2+ artifact")
```

### Step 3: Validate Each Question

```python
questions = parse_questions(open_questions_section)

for question in questions:
    # Check for standardized marker
    marker = extract_marker(question)  # e.g., "[REQUIRES SPIKE]"

    if marker is None:
        errors.append(f"Question missing marker: {question.text}")
        continue

    # Validate marker is allowed for this artifact type
    allowed_markers = get_allowed_markers(artifact_type)  # e.g., ["[REQUIRES SPIKE]", "[REQUIRES ADR]", ...]

    if marker not in allowed_markers:
        errors.append(f"Invalid marker {marker} for {artifact_type}. Allowed: {allowed_markers}")
        continue

    # Validate required sub-fields
    required_fields = get_required_fields(marker)  # e.g., ["Investigation Needed", "Spike Scope", "Time Box", "Blocking"]

    for field in required_fields:
        if not has_field(question, field):
            errors.append(f"Marker {marker} missing required sub-field: {field}")
```

### Step 4: Check for Prohibited Patterns

```python
# Check for free-form text patterns
prohibited_patterns = [
    r"Decision:\s*\w+\s*needed",
    r"Action Required:\s*(?!.*ACTION REQUIRED)",  # Allow meta-instruction only
]

for pattern in prohibited_patterns:
    matches = re.findall(pattern, open_questions_section)
    if matches:
        errors.append(f"Prohibited free-form text pattern found: {matches[0]}")
```

### Step 5: Return Validation Result

```python
if errors:
    return ValidationResult(
        valid=False,
        errors=errors,
        artifact_id=artifact.id,
        version=version
    )
else:
    return ValidationResult(valid=True)
```

---

## Generator Updates Required

| Generator | Priority | Estimated Effort |
|-----------|----------|------------------|
| Epic Generator | High | 2-3 hours |
| PRD Generator | High | 2-3 hours |
| HLS Generator | High | 2-3 hours |
| Backlog Story Generator | **Critical** | 3-4 hours (includes US-030 example) |
| Tech Spec Generator | Medium | 2-3 hours |
| Implementation Task Generator | Medium | 2-3 hours |

**Total Estimated Effort:** 14-20 hours for all generators

---

## Testing Validation Logic

### Test Cases by Artifact Type

**Epic Generator Tests:**
1. ✅ v1 artifact with free-form questions → PASS (no validation)
2. ✅ v2 artifact with valid `[REQUIRES EXECUTIVE DECISION]` marker + all sub-fields → PASS
3. ❌ v2 artifact with question missing marker → FAIL
4. ❌ v2 artifact with marker missing sub-fields → FAIL
5. ❌ v2 artifact with "Decision: X needed" free-form text → FAIL

**Backlog Story Generator Tests (US-030 Example):**
1. ✅ v1 artifact with recommendations → PASS
2. ✅ v2 artifact with valid `[REQUIRES SPIKE]` marker + all sub-fields → PASS
3. ❌ v2 artifact with "Decision: Spike needed" free-form text → FAIL
4. ❌ v2 artifact with marker missing "Time Box" sub-field → FAIL
5. ❌ v2 artifact with Time Box > 3 days → FAIL

**Repeat similar test structure for all generators.**

---

## Rollout Plan

**Phase 1 (Week 1):**
- Implement validation for Backlog Story Generator (critical - US-030 example)
- Test on US-030 v2 correction

**Phase 2 (Week 2):**
- Implement validation for Epic, PRD, HLS Generators
- Test on existing v2 artifacts

**Phase 3 (Week 3):**
- Implement validation for Tech Spec, Implementation Task Generators
- Full integration testing

**Phase 4 (Week 4):**
- Documentation update
- Team training on marker system enforcement

---

## Related Documents

- **CLAUDE.md:** Open Questions Marker System section (lines ~479-698)
- **Lean Analysis Report:** v1.4 Recommendation 5 (lines ~1359-1743)
- **Templates:** All updated templates (Epic v1.6, PRD v1.9, HLS v1.6, US v1.9, Tech Spec v1.3, Task v1.3)

---

**Document Version:** 1.0
**Last Updated:** 2025-10-20
**Maintained By:** Context Engineering PoC Team

# Input Classification Inconsistency Analysis

**Date:** 2025-10-13
**Purpose:** Analyze current required/optional input definitions across all generators and compare with CLAUDE.md dependency tree to identify inconsistencies

---

## Executive Summary

**Total Generators Analyzed:** 12
**Major Inconsistencies Found:** 15+
**Categories of Issues:**
1. **Attribute Mismatch**: Generator says `required="true"` but CLAUDE.md says "(optional)"
2. **Semantic Confusion**: Description text says "optional" or "if available" but attribute says `required="true"`
3. **Missing Terminology**: No clear distinction between "Secondary Input (optional)" vs truly mandatory inputs
4. **PRD Generator Unique Case**: Has THREE inputs (Epic + both research types), but all marked `required="true"` when CLAUDE.md says research is optional

---

## Generator-by-Generator Comparison

### 1. Product Vision Generator

**CLAUDE.md says (lines 76-78):**
- Business Research: `Input` (no "Primary" designation, no "(optional)" notation)

**Generator says (lines 47-59):**
- Business Research: `required="true"`
- Description: No mention of "optional"

**Inconsistency:** ✅ **MATCH** - CLAUDE.md shows single required input, generator implements it as required

---

### 2. Initiative Generator

**CLAUDE.md says (lines 84-86):**
- Product Vision: `Primary Input` (approved)
- Business Research: `Secondary Input: artifacts/research/{product_name}_business_research.md (optional)`

**Generator says (lines 39-58):**
- Product Vision: `required="true"` ✅
- Business Research: `required="false"` ✅
- Business Research description says: "**If available**, Business Research provides..."

**Inconsistency:** ✅ **MATCH** - Properly implements Primary (required) vs Secondary (optional)

---

### 3. Epic Generator

**CLAUDE.md says (lines 89-91):**
- Product Vision: `Primary Input` (approved)
- Business Research: `Secondary Input: artifacts/research/{product_name}_business_research.md (optional)`

**Generator says (lines 43-70):**
- Product Vision: `required="true"` (lines 43-48)
- Initiative: `required="true"` (lines 54-60) ⚠️
- Business Research: `required="false"` (lines 62-70)

**Inconsistency:** ⚠️ **PARTIAL MATCH**
- Product Vision correctly marked required
- Business Research correctly marked optional
- **ISSUE**: Initiative marked `required="true"` but CLAUDE.md doesn't mention Initiative as input at all (only Product Vision). Epic OR Initiative should be mutually exclusive, not both required.
- Line 7 metadata says: `depends_on>Product Vision OR Initiative` (OR, not both)
- Description text says "If available" for Business Research ✅

---

### 4. PRD Generator

**CLAUDE.md says (lines 97-100):**
- Epic: `Primary Input` (approved)
- Business Research: `Secondary Input 1: artifacts/research/{product_name}_business_research.md (optional - market validation)`
- Implementation Research: `Secondary Input 2: artifacts/research/{product_name}_implementation_research.md (optional - technical feasibility)`

**Generator says (lines 42-75):**
- Epic: `required="true"` (lines 42-52) ✅
- Business Research: `required="true"` (lines 54-64) ❌
- Implementation Research: `required="true"` (lines 66-75) ❌

**Inconsistency:** ❌ **MAJOR MISMATCH**
- Epic correctly marked required
- **CRITICAL ISSUE**: Both research documents marked `required="true"` but CLAUDE.md explicitly says "(optional)"
- Description text DOES acknowledge optionality:
  - Line 32: "PRD loads BOTH research types:" (implies may not load)
  - Business Research description uses functional language but no "if available"
  - Implementation Research description uses functional language but no "if available"
- **CONTRADICTION**: required="true" contradicts optional usage pattern in CLAUDE.md

---

### 5. High-Level Story Generator

**CLAUDE.md says (lines 102-104):**
- PRD: `Primary Input` (approved)
- Business Research: `Secondary Input: artifacts/research/{product_name}_business_research.md (optional)`

**Generator says (lines 43-70):**
- Epic: `required="true"` (lines 43-50) - mutually exclusive with PRD
- PRD: `required="true"` (lines 52-60) - mutually exclusive with Epic
- Business Research: `required="true"` (lines 62-70) ❌

**Inconsistency:** ❌ **MAJOR MISMATCH**
- **CRITICAL ISSUE**: Business Research marked `required="true"` but CLAUDE.md says "(optional)"
- Description text says: "Business Research provides (BUSINESS PERSPECTIVE ONLY):" - no "if available"
- Epic vs PRD mutual exclusivity is fine (line 7: `depends_on>Epic OR PRD`)

---

### 6. Backlog Story Generator

**CLAUDE.md says (lines 109-111):**
- PRD: `Primary Input` (approved)
- Implementation Research: `Secondary Input: artifacts/research/{product_name}_implementation_research.md (optional)`

**Generator says (lines 43-71):**
- High-Level Story: `required="true"` (lines 43-51) ✅
- Implementation Research: `required="true"` (lines 53-62) ❌
- PRD: `required="false"` (lines 64-71) ⚠️

**Inconsistency:** ❌ **MAJOR MISMATCH**
- High-Level Story correctly marked required
- **CRITICAL ISSUE**: Implementation Research marked `required="true"` but CLAUDE.md says "(optional)"
- Description says: "Implementation Research provides (TECHNICAL PERSPECTIVE):" - no "if available"
- **PRD ISSUE**: PRD marked `required="false"` but CLAUDE.md says PRD is Primary Input (should be required). Description says "if needed for context" which suggests optional, but this contradicts CLAUDE.md.

**UPDATE:** Re-reading CLAUDE.md line 109: "Primary Input: artifacts/prds/PRD-{XXX}_prd_v{N}.md (approved)" - but Backlog Story has High-Level Story as parent, not PRD directly. This is confusing. High-Level Story is parent, PRD is grandparent. Generator correctly makes PRD optional since High-Level Story is the direct parent.

---

### 7. Spike Generator

**CLAUDE.md says (lines 117-119):**
- Backlog Story: `Primary Input` (question marked [REQUIRES SPIKE])
- Tech Spec: `Alternative Input` (Open Questions)
- Implementation Research: `Secondary Input: artifacts/research/{product_name}_implementation_research.md (optional - baseline data)`

**Generator says (lines 46-63):**
- Backlog Story: `required="true"` (lines 46-49) - mutually exclusive with Tech Spec
- Tech Spec: `required="true"` (lines 51-54) ❌ - mutually exclusive with Backlog Story
- Implementation Research: `required="false"` (lines 56-63) ✅

**Inconsistency:** ⚠️ **PARTIAL MATCH**
- Backlog Story correctly marked required
- Implementation Research correctly marked optional with "OPTIONAL" in description ✅
- **ISSUE**: Tech Spec marked `required="true"` but should be mutually exclusive (OR relationship). Line 7: `depends_on>Backlog Story OR Technical Specification` suggests OR, not both required.
- Description for Implementation Research says: "Implementation Research provides (OPTIONAL):" ✅

---

### 8. ADR Generator

**CLAUDE.md says (lines 125-128):**
- Backlog Story: `Primary Input`
- Spike: `Optional Input` (if spike completed - provides findings and evidence)
- Implementation Research: `Secondary Input`

**Generator says (lines 46-65):**
- Backlog Story: `required="true"` (lines 46-49) ✅
- Spike: `required="false"` (lines 51-55) ✅
- Implementation Research: `required="false"` (lines 57-65) ❌

**Inconsistency:** ⚠️ **PARTIAL MATCH**
- Backlog Story correctly marked required
- Spike correctly marked optional ✅
- **ISSUE**: Implementation Research marked `required="false"` but CLAUDE.md says "Secondary Input" without "(optional)" - implies should be required
- However, description doesn't say "if available", just describes what it provides
- **AMBIGUITY**: "Secondary Input" terminology unclear - does it mean optional or mandatory?

---

### 9. Tech Spec Generator

**CLAUDE.md says (lines 131-134):**
- Backlog Story: `Primary Input`
- Spike: `Optional Input` (if spike completed - provides implementation details)
- Implementation Research: `Secondary Input`

**Generator says (lines 38-49):**
- Backlog Story: `required="true"` (line 38) ✅
- Implementation Research: `required="true"` (line 42) ✅
- ADR: `required="true"` (line 47) ⚠️

**Inconsistency:** ⚠️ **PARTIAL MATCH**
- Backlog Story correctly marked required
- Implementation Research marked required - matches "Secondary Input" if we interpret as mandatory ✅
- **MISSING**: Spike not listed as input artifact at all, but CLAUDE.md says "Optional Input"
- **ADR ISSUE**: ADR marked `required="true"` but CLAUDE.md doesn't list ADR as input (line 7 metadata mentions it though)
- No "if available" language in descriptions

---

### 10. Business Research Generator

**CLAUDE.md says (lines 68-71):**
- No inputs from artifacts (root research phase)
- Human inputs: product idea, problem overview, target users, key capabilities, constraints, product references

**Generator says (lines 63-72):**
- Only human interactive input
- No `required` attribute (not applicable for human inputs)

**Inconsistency:** ✅ **MATCH** - Correctly implements human input collection

---

### 11. Implementation Research Generator

**CLAUDE.md says (lines 68-71):**
- No inputs from artifacts (root research phase)
- Human inputs: product idea, technical challenges, scale requirements, performance targets, product references

**Generator says (lines 63-71):**
- Only human interactive input
- No `required` attribute (not applicable for human inputs)

**Inconsistency:** ✅ **MATCH** - Correctly implements human input collection

---

### 12. Implementation Task Generator

**NOTE:** Not analyzed in detail as it's not in CLAUDE.md dependency tree (lines 64-156). This generator exists but is not documented in the dependency tree section.

---

## Summary Table

| Generator | Input | CLAUDE.md Classification | Generator Attribute | Generator Description | Match? |
|-----------|-------|--------------------------|---------------------|-----------------------|--------|
| **Product Vision** | Business Research | Input (implied required) | `required="true"` | Functional | ✅ |
| **Initiative** | Product Vision | Primary Input | `required="true"` | Functional | ✅ |
| **Initiative** | Business Research | Secondary Input (optional) | `required="false"` | "If available" | ✅ |
| **Epic** | Product Vision | Primary Input | `required="true"` | Functional | ✅ |
| **Epic** | Initiative | Not mentioned | `required="true"` | Functional | ⚠️ |
| **Epic** | Business Research | Secondary Input (optional) | `required="false"` | "If available" | ✅ |
| **PRD** | Epic | Primary Input | `required="true"` | Functional | ✅ |
| **PRD** | Business Research | Secondary Input 1 (optional) | `required="true"` | Functional (no "if available") | ❌ |
| **PRD** | Implementation Research | Secondary Input 2 (optional) | `required="true"` | Functional (no "if available") | ❌ |
| **High-Level Story** | PRD | Primary Input | `required="true"` | Functional | ✅ |
| **High-Level Story** | Business Research | Secondary Input (optional) | `required="true"` | Functional (no "if available") | ❌ |
| **Backlog Story** | High-Level Story | Implicit Primary | `required="true"` | Functional | ✅ |
| **Backlog Story** | Implementation Research | Secondary Input (optional) | `required="true"` | Functional (no "if available") | ❌ |
| **Backlog Story** | PRD | Not Primary (grandparent) | `required="false"` | "if needed for context" | ✅ |
| **Spike** | Backlog Story | Primary Input | `required="true"` | Functional | ✅ |
| **Spike** | Tech Spec | Alternative Input | `required="true"` | Functional | ⚠️ |
| **Spike** | Implementation Research | Secondary Input (optional) | `required="false"` | "(OPTIONAL)" | ✅ |
| **ADR** | Backlog Story | Primary Input | `required="true"` | Functional | ✅ |
| **ADR** | Spike | Optional Input | `required="false"` | Functional | ✅ |
| **ADR** | Implementation Research | Secondary Input | `required="false"` | Functional | ⚠️ |
| **Tech Spec** | Backlog Story | Primary Input | `required="true"` | Functional | ✅ |
| **Tech Spec** | Implementation Research | Secondary Input | `required="true"` | Functional | ✅ |
| **Tech Spec** | Spike | Optional Input | Not listed | N/A | ❌ |
| **Tech Spec** | ADR | Not mentioned in CLAUDE.md | `required="true"` | Functional | ⚠️ |

**Legend:**
- ✅ = Consistent between CLAUDE.md and generator
- ❌ = Major inconsistency (required vs optional mismatch)
- ⚠️ = Partial match or ambiguity

---

## Key Findings

### 1. Total Inconsistencies Found: 15

**Major Issues (required="true" but CLAUDE.md says optional):**
1. PRD → Business Research (should be optional)
2. PRD → Implementation Research (should be optional)
3. High-Level Story → Business Research (should be optional)
4. Backlog Story → Implementation Research (should be optional)

**Mutual Exclusivity Issues (both marked required when should be OR):**
5. Epic → Product Vision OR Initiative (both marked required)
6. Spike → Backlog Story OR Tech Spec (both marked required)

**Missing Inputs:**
7. Tech Spec missing Spike as optional input

**Ambiguous Classification (Secondary Input without "(optional)" notation):**
8. ADR → Implementation Research (Secondary Input ambiguous)
9. Tech Spec → ADR (not in CLAUDE.md dependency tree)

---

### 2. Generators with Most Issues

**PRD Generator (3 issues):**
- Both research inputs marked required when should be optional
- This is the most critical issue as PRD is a bridge artifact

**Tech Spec Generator (2 issues):**
- Missing Spike as optional input
- ADR not documented in CLAUDE.md but present in generator

**Epic Generator (1 issue):**
- Initiative marked required when should be mutually exclusive with Product Vision

**Spike Generator (1 issue):**
- Tech Spec marked required when should be mutually exclusive with Backlog Story

---

### 3. Semantic Confusion Examples

**Good examples (clear optionality):**
- Initiative → Business Research: `required="false"` + description says "**If available**, Business Research provides..."
- Spike → Implementation Research: `required="false"` + description says "Implementation Research provides (OPTIONAL):"

**Confusing examples (semantic mismatch):**
- PRD → Business Research: `required="true"` + description says "Business Research provides (BUSINESS PERSPECTIVE):" - no "if available" marker
- High-Level Story → Business Research: `required="true"` + description says "Business Research provides (BUSINESS PERSPECTIVE ONLY):" - no "if available"

---

### 4. Missing from CLAUDE.md

**Inputs present in generators but not in CLAUDE.md dependency tree:**
- Tech Spec → ADR (generator has it, CLAUDE.md doesn't mention it)

**Generators present but not in dependency tree:**
- Implementation Task Generator (exists but not documented in lines 64-156)

---

### 5. "Secondary Input" Terminology Ambiguity

**CLAUDE.md uses two patterns:**

**Pattern 1: Secondary Input with "(optional)"**
- Initiative → Business Research: "Secondary Input: ... (optional)"
- Epic → Business Research: "Secondary Input: ... (optional)"
- PRD → Business Research: "Secondary Input 1: ... (optional - market validation)"
- PRD → Implementation Research: "Secondary Input 2: ... (optional - technical feasibility)"

**Pattern 2: Secondary Input without "(optional)"**
- ADR → Implementation Research: "Secondary Input: ..." (no "(optional)" notation)
- Tech Spec → Implementation Research: "Secondary Input: ..." (no "(optional)" notation)

**Question:** Does "Secondary Input" without "(optional)" mean:
- A) Mandatory (load every time)
- B) Optional (load when enrichment needed per CLAUDE.md line 151)
- C) Recommended (should load unless reason not to)

**CLAUDE.md line 151 clarification:**
> "Secondary inputs are OPTIONAL: Load when enrichment needed, not by default"

This suggests ALL "Secondary Input" entries are optional, regardless of "(optional)" notation.

**However, generators interpret differently:**
- ADR Generator: Implementation Research `required="false"` (interprets as optional)
- Tech Spec Generator: Implementation Research `required="true"` (interprets as mandatory)

---

## Recommended 3-Tier Classification System

Based on analysis and CLAUDE.md line 151 ("Secondary inputs are OPTIONAL: Load when enrichment needed, not by default"), I recommend:

### Tier 1: **mandatory**
**Definition:** Artifact MUST be loaded for generator to function. Generator cannot proceed without it.

**Characteristics:**
- Direct parent in dependency chain
- Contains core requirements for output artifact
- Marked in CLAUDE.md as "Primary Input" or single "Input"
- Blocking: Generator fails if not provided

**Which inputs qualify:**
1. Product Vision → Business Research (only input)
2. Initiative → Product Vision (Primary Input)
3. Epic → Product Vision (Primary Input)
4. PRD → Epic (Primary Input)
5. High-Level Story → PRD (Primary Input)
6. Backlog Story → High-Level Story (direct parent)
7. Spike → Backlog Story OR Tech Spec (Primary/Alternative)
8. ADR → Backlog Story (Primary Input)
9. Tech Spec → Backlog Story (Primary Input)
10. Tech Spec → Implementation Research (core technical reference)

**Recommended attribute:** `required="true"`

---

### Tier 2: **recommended**
**Definition:** Artifact SHOULD be loaded to produce high-quality output, but generator can function without it by making reasonable inferences or noting gaps.

**Characteristics:**
- Enriches output with additional context
- Marked in CLAUDE.md as "Secondary Input (optional)"
- Absence causes quality degradation but not failure
- Generator should note when not loaded: "Business Research not available - recommendations based on Epic only"
- Should be loaded by default in standard workflow, skipped only when explicitly unavailable

**Which inputs qualify:**
1. Initiative → Business Research (Secondary Input - optional)
2. Epic → Business Research (Secondary Input - optional)
3. PRD → Business Research (Secondary Input 1 - optional)
4. PRD → Implementation Research (Secondary Input 2 - optional)
5. High-Level Story → Business Research (Secondary Input - optional)
6. Backlog Story → Implementation Research (Secondary Input - optional)
7. Spike → Implementation Research (Secondary Input - optional)
8. ADR → Implementation Research (Secondary Input)

**Recommended attribute:** `required="false"` OR new `recommended="true"`

**Load behavior:**
- Attempt to load by default
- If not found, log warning: "[WARN] Implementation Research not found - proceeding without technical context"
- Continue execution, note gaps in output

---

### Tier 3: **conditional**
**Definition:** Artifact is loaded ONLY under specific conditions or when explicitly requested.

**Characteristics:**
- Marked in CLAUDE.md as "Optional Input" (not "Secondary Input")
- Loaded conditionally based on:
  - Spike results available → ADR/Tech Spec load spike
  - Additional context needed → load PRD from Backlog Story
  - Investigation outcome → load research
- Not loaded by default
- Presence/absence doesn't affect quality (provides alternative path)

**Which inputs qualify:**
1. ADR → Spike (Optional Input - if spike completed)
2. Tech Spec → Spike (Optional Input - if spike completed)
3. Backlog Story → PRD (optional for additional context - parent is High-Level Story)

**Recommended attribute:** `conditional="true"` OR keep `required="false"` with conditional logic

**Load behavior:**
- Check condition first
- Load only if condition met or explicitly requested
- No warning if not loaded (expected behavior)

---

### Tier 4: **mutually_exclusive** (Special case)
**Definition:** One of N inputs must be provided, but not all.

**Characteristics:**
- Marked in CLAUDE.md with "OR" relationship (metadata `depends_on` uses OR)
- Generator validates exactly one is provided
- Examples: Epic (Product Vision OR Initiative), Spike (Backlog Story OR Tech Spec)

**Which inputs qualify:**
1. Epic → Product Vision OR Initiative (either required)
2. High-Level Story → Epic OR PRD (either required)
3. Spike → Backlog Story OR Tech Spec (either required)

**Recommended attribute:** `required="true" mutually_exclusive_group="A"`

**Validation:**
- At least one input from group must be provided
- Only one input from group should be provided (or handle both gracefully)

---

## Recommended Changes by Generator

### PRD Generator
**Current:**
- Epic: `required="true"` ✅
- Business Research: `required="true"` ❌
- Implementation Research: `required="true"` ❌

**Recommended:**
- Epic: `required="true"` (Tier 1: mandatory)
- Business Research: `recommended="true"` (Tier 2: recommended)
- Implementation Research: `recommended="true"` (Tier 2: recommended)

**Rationale:** CLAUDE.md line 98-99 explicitly says "(optional - market validation)" and "(optional - technical feasibility)"

---

### High-Level Story Generator
**Current:**
- Epic: `required="true"` (mutually exclusive with PRD)
- PRD: `required="true"` (mutually exclusive with Epic)
- Business Research: `required="true"` ❌

**Recommended:**
- Epic: `required="true" mutually_exclusive_group="parent"` (Tier 4)
- PRD: `required="true" mutually_exclusive_group="parent"` (Tier 4)
- Business Research: `recommended="true"` (Tier 2: recommended)

**Rationale:** CLAUDE.md line 103 says "(optional)"

---

### Backlog Story Generator
**Current:**
- High-Level Story: `required="true"` ✅
- Implementation Research: `required="true"` ❌
- PRD: `required="false"` ✅

**Recommended:**
- High-Level Story: `required="true"` (Tier 1: mandatory)
- Implementation Research: `recommended="true"` (Tier 2: recommended)
- PRD: `conditional="true"` (Tier 3: conditional - for additional context)

**Rationale:** CLAUDE.md line 110 says Implementation Research is "(optional)"

---

### Spike Generator
**Current:**
- Backlog Story: `required="true"` (mutually exclusive)
- Tech Spec: `required="true"` (mutually exclusive) ❌
- Implementation Research: `required="false"` ✅

**Recommended:**
- Backlog Story: `required="true" mutually_exclusive_group="source"` (Tier 4)
- Tech Spec: `required="true" mutually_exclusive_group="source"` (Tier 4)
- Implementation Research: `recommended="true"` (Tier 2: recommended)

**Rationale:** Both should be mutually exclusive (OR relationship), Implementation Research optional

---

### ADR Generator
**Current:**
- Backlog Story: `required="true"` ✅
- Spike: `required="false"` ✅
- Implementation Research: `required="false"` ⚠️

**Recommended:**
- Backlog Story: `required="true"` (Tier 1: mandatory)
- Spike: `conditional="true"` (Tier 3: conditional - if spike completed)
- Implementation Research: `recommended="true"` (Tier 2: recommended)

**Rationale:** CLAUDE.md line 127 says "Secondary Input" without "(optional)", but line 151 says all Secondary Inputs are optional. Upgrade to recommended.

---

### Tech Spec Generator
**Current:**
- Backlog Story: `required="true"` ✅
- Implementation Research: `required="true"` ✅
- ADR: `required="true"` ⚠️
- Spike: Not listed ❌

**Recommended:**
- Backlog Story: `required="true"` (Tier 1: mandatory)
- Implementation Research: `required="true"` (Tier 1: mandatory - core technical reference)
- ADR: `recommended="true"` (Tier 2: recommended - documents decisions)
- Spike: `conditional="true"` (Tier 3: conditional - if spike completed)

**Rationale:**
- Implementation Research is essential for technical specs (not just enrichment)
- ADR should be recommended (documents major decisions affecting spec)
- Spike should be conditional input per CLAUDE.md line 132

---

### Epic Generator
**Current:**
- Product Vision: `required="true"` ✅
- Initiative: `required="true"` ❌
- Business Research: `required="false"` ✅

**Recommended:**
- Product Vision: `required="true" mutually_exclusive_group="parent"` (Tier 4)
- Initiative: `required="true" mutually_exclusive_group="parent"` (Tier 4)
- Business Research: `recommended="true"` (Tier 2: recommended)

**Rationale:** Product Vision OR Initiative (not both), Business Research optional

---

## Implementation Strategy

### Phase 1: Align Critical Mismatches
**Priority:** HIGH
**Generators to fix:**
1. PRD Generator (2 research inputs)
2. High-Level Story Generator (Business Research)
3. Backlog Story Generator (Implementation Research)

**Changes:**
- Change `required="true"` to `required="false"` for all Secondary Input (optional) entries
- Add "if available" language to descriptions

---

### Phase 2: Implement 3-Tier System
**Priority:** MEDIUM
**Scope:** All generators

**Add new attributes:**
```xml
<artifact
  required="true|false"
  recommended="true|false"
  conditional="true|false"
  mutually_exclusive_group="string"
  type="artifact_type">
```

**Migration:**
- `required="true"` (Primary Input) → `required="true"`
- `required="false"` (Secondary Input optional) → `recommended="true"`
- `required="false"` (Optional Input) → `conditional="true"`
- Mutual exclusivity → `mutually_exclusive_group="name"`

---

### Phase 3: Update CLAUDE.md Terminology
**Priority:** MEDIUM
**Changes:**

Replace ambiguous terminology:
- "Primary Input" → "Mandatory Input"
- "Secondary Input (optional)" → "Recommended Input (enrichment)"
- "Optional Input" → "Conditional Input (if available)"
- "Alternative Input" → "Mutually Exclusive Input"

Add explicit table:
```markdown
## Input Classification Legend

| Term | Meaning | Generator Behavior | Example |
|------|---------|-------------------|---------|
| Mandatory Input | Must be provided | Fails if missing | PRD → Epic |
| Recommended Input | Should be loaded | Warns if missing, continues | PRD → Business Research |
| Conditional Input | Load only if condition met | No warning if absent | ADR → Spike |
| Mutually Exclusive Input | One of N required | Validates exactly one provided | Epic → Vision OR Initiative |
```

---

### Phase 4: Add Load Behavior Documentation
**Priority:** LOW
**Scope:** Each generator

Document in generator `<instructions>`:
```xml
<step priority="N">
  <action>Load [Artifact] (recommended)</action>
  <load_behavior>
    - Attempt to load from standard path
    - If not found, log warning: "[WARN] Business Research not available - proceeding without market context"
    - Continue execution
    - Note gaps in output: "Market analysis limited - Business Research not available"
  </load_behavior>
</step>
```

---

## Validation Questions

1. **For CLAUDE.md "Secondary Input" without "(optional)" (ADR/Tech Spec → Implementation Research):**
   - Should these be mandatory or recommended?
   - Current interpretation: ADR says optional, Tech Spec says required
   - Recommendation: Make recommended (Tier 2) for consistency with line 151

2. **For mutual exclusivity (Epic, High-Level Story, Spike):**
   - Should generators accept both inputs and choose, or validate only one provided?
   - Recommendation: Accept both, use precedence order (e.g., PRD over Epic)

3. **For PRD being grandparent of Backlog Story:**
   - Should Backlog Story load PRD directly, or only through High-Level Story?
   - Current: PRD marked `required="false"` in Backlog Story
   - Recommendation: Keep conditional - load only when High-Level Story lacks context

4. **For Tech Spec → ADR dependency:**
   - Should this be added to CLAUDE.md dependency tree?
   - Tech Spec should reference ADR decisions
   - Recommendation: Add to CLAUDE.md, mark as recommended input

---

## Next Steps

1. **Review this report** with framework stakeholders
2. **Decide on 3-tier system** (mandatory/recommended/conditional) vs simpler required/optional
3. **Create consolidated fix** addressing all PRD Generator research input issues (highest priority)
4. **Update CLAUDE.md** terminology for clarity
5. **Generate updated generator prompts** with consistent input classification
6. **Add validation rules** to `/generate` command to check input requirements

---

**End of Report**

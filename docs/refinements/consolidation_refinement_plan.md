# CLAUDE.md Consolidation Refinement Plan

**Issue**: Redundant path and dependency information across multiple sections
**Priority**: High (affects maintainability and error rate)
**Date**: 2025-10-13
**Status**: Proposed

---

## Problem Analysis

### 1. Path Definition Redundancy

**Current State:**
- Paths defined in 3 locations:
  - "Folder Structure" section (lines ~13-50)
  - "Artifact Path Patterns" section (lines ~350-400)
  - "SDLC Generators Input Dependency Tree" section (lines ~100-180)

**Problems:**
- **Maintenance Burden**: Any path change requires updates in 3 places
- **Error-Prone**: Inconsistencies between sections cause generator failures
- **Cognitive Load**: Readers must check multiple sections to understand path structure

**Impact**: High - affects all 12 generators

---

### 2. Dependency Information Duplication

**Current State:**
- Input dependencies defined in 2 locations:
  - Each generator's `<input_artifacts>` section (with classification, paths, naming)
  - "SDLC Generators Input Dependency Tree" section (comprehensive view)

**Questions:**
- Does the Dependency Tree add unique value beyond generator definitions?
- Is the comprehensive view worth maintaining separately?

**Analysis:**
| Information Type | In Generators | In Dependency Tree | Value of Duplication |
|------------------|---------------|-------------------|---------------------|
| Input artifact paths | ✓ (detailed) | ✓ (visual) | LOW - creates sync burden |
| Classification (mandatory/recommended) | ✓ (authoritative) | ✗ (not shown) | N/A |
| Dependency relationships | ✓ (implicit) | ✓ (explicit visual) | **HIGH** - visual flow aids understanding |
| Conditional logic | ✓ (detailed) | ✓ (annotated) | MEDIUM - annotations help comprehension |

**Recommendation:** Reduce duplication while preserving high-value visual dependency flow

---

### 3. Folder Structure vs. File Naming Conventions

**Current State:**
- "Folder Structure" section includes file naming patterns (e.g., `VIS-{XXX}_product_vision_v{N}.md`)
- "File Naming Conventions" section duplicates these patterns with additional detail

**Overlap Analysis:**
- Folder Structure shows: Directory hierarchy + file name examples
- File Naming Conventions shows: File name patterns + variable explanations
- Redundancy: ~60% overlap in file naming information

---

## Proposed Solution

### Phase 1: Path Consolidation (High Priority)

**Goal:** Single source of truth for all file paths

**Approach:** Enhance "Artifact Path Patterns" section as canonical reference

**Structure:**
```markdown
## Artifact Path Patterns (Single Source of Truth)

**Path Variables:**
- {id} - Artifact ID (e.g., 005, 042, 123)
- {version} - Version number (1, 2, 3)
- {product_name} - Product name for research documents
- {feature_name} - Feature name for backlog stories

**Template Paths:**
- Product Vision: prompts/templates/product-vision-template.xml
- Epic: prompts/templates/epic-template.xml
[... all template paths ...]

**Generator Paths:**
- Product Vision: prompts/product-vision-generator.xml
[... all generator paths ...]

**Input Artifact Paths:**
- Product Vision: artifacts/product_visions/VIS-{id}_product_vision_v{version}.md
[... all artifact paths ...]

**Output Artifact Paths:**
[same as input, for clarity]

**Usage in Generators:**
"Load template from path defined in CLAUDE.md Artifact Path Patterns for [artifact type]"
```

**Changes Required:**
1. ✓ Keep enhanced "Artifact Path Patterns" section (already exists)
2. Simplify "Folder Structure" to directory hierarchy only (no file names)
3. Remove path details from "SDLC Generators Input Dependency Tree"
4. Update all generator references to cite "Artifact Path Patterns"

---

### Phase 2: Dependency Tree Simplification (Medium Priority)

**Goal:** Preserve visual flow, eliminate redundant details

**Approach:** Transform to high-level relationship diagram with minimal metadata

**New Structure:**
```markdown
## SDLC Artifact Dependency Flow

Visual representation of input/output relationships. For detailed paths and classification, see:
- Paths: "Artifact Path Patterns" section
- Classification rules: "Input Classification System" section
- Detailed inputs: Each generator's <input_artifacts> section

```
Research Phase (Root)
├── Business Research → Vision/Strategic artifacts
└── Implementation Research → Technical artifacts

↓

Vision Phase
└── Product Vision
    └── Input: Business Research

↓

Strategic Phase
├── Initiative (requires: Product Vision XOR Initiative)
└── Epic (requires: Product Vision)

[... simplified flow with minimal annotations ...]
```

**Rationale:** Provides 10,000-foot view without duplicating details maintained elsewhere

---

### Phase 3: Folder Structure vs. File Naming (Low Priority)

**Goal:** Clear separation of concerns

**Option A: Merge into Folder Structure**
```markdown
## Folder Structure

/artifacts/
   product_visions/
      VIS-{XXX}_product_vision_v{N}.md    # VIS-XXX = Vision ID, N = version (1-3)
   epics/
      EPIC-{XXX}_epic_v{N}.md              # EPIC-XXX = Epic ID, N = version (1-3)
[...]
```
- **Pros:** Single reference for location + naming
- **Cons:** Verbose, harder to scan directory structure

**Option B: Keep Separate (Current)**
- **Pros:** Easier to scan directory hierarchy
- **Cons:** Duplication between sections

**Recommendation:** **Option A** - merge naming conventions inline with folder structure as comments

---

## Implementation Plan

### Step 1: Validate Current "Artifact Path Patterns" Section
- [x] Verify all 12 artifact types covered
- [x] Ensure all path variables documented
- [x] Confirm generator/template/artifact paths complete

### Step 2: Update "Folder Structure" Section
- [ ] Remove file naming patterns (keep directory structure only)
- [ ] Add inline comments with naming conventions where helpful
- [ ] Add reference pointer: "For complete path patterns, see Artifact Path Patterns section"

### Step 3: Simplify "SDLC Generators Input Dependency Tree"
- [ ] Rename to "SDLC Artifact Dependency Flow"
- [ ] Remove detailed path information (reference Artifact Path Patterns)
- [ ] Preserve visual flow and critical annotations (classification, conditions)
- [ ] Add header linking to detailed sections

### Step 4: Remove "File Naming Conventions" Section
- [ ] Merge unique information into "Folder Structure" or "Artifact Path Patterns"
- [ ] Delete standalone section

### Step 5: Update All Generator References
- [ ] Search generators for hardcoded paths
- [ ] Replace with references: "See CLAUDE.md Artifact Path Patterns for [type]"
- [ ] Validate all generators still function

### Step 6: Validation
- [ ] Run all generators with test inputs
- [ ] Verify path resolution works correctly
- [ ] Check for broken references in documentation

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Generators fail to find paths after refactor | Medium | High | Thorough testing with each generator before deployment |
| Users confused by new structure | Low | Medium | Add clear navigation pointers between sections |
| Information lost during consolidation | Low | High | Detailed review of merged content before deletion |
| Ongoing edits conflict with refactor | Medium | Low | Communicate refactor plan, merge carefully |

---

## Success Criteria

1. **Single Source of Truth**: All paths defined once in "Artifact Path Patterns"
2. **Zero Redundancy**: No path/naming information duplicated across sections
3. **Functional Generators**: All 12 generators execute successfully with test inputs
4. **Improved Maintainability**: Path changes require editing 1 section (not 3)
5. **Clear Navigation**: Users can find path/dependency information quickly (<30 seconds)

---

## Estimated Effort

- **Phase 1**: 2-3 hours (path consolidation)
- **Phase 2**: 1-2 hours (dependency tree simplification)
- **Phase 3**: 1 hour (folder structure cleanup)
- **Total**: 4-6 hours

---

## Next Actions

1. Review this plan with stakeholders
2. Approve Phase 1 for immediate implementation (highest ROI)
3. Schedule Phases 2-3 based on priority
4. Create backup branch before making changes
5. Execute Step 1 (validate current Artifact Path Patterns)

---

**Document Owner**: Context Engineering PoC Team
**Review Date**: 2025-10-20
**Related Issues**: #2 (Path Consolidation), #3 (Input Classification)

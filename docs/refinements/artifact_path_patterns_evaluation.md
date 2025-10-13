# Artifact Path Patterns Section - Value Evaluation

**Date**: 2025-10-13
**Issue**: Potential redundancy between "Folder Structure" and "Artifact Path Patterns" sections

---

## Current State

### Folder Structure Section (lines 8-72)
**Format**: Tree view with patterns + inline examples
```
artifacts/
   product_visions/
      VIS-{XXX}_product_vision_v{N}.md    # Format: VIS-001_product_vision_v1.md
   prompts/
      templates/
         {artifact-type}-template.xml     # Format: prd-template.xml
```

**Variables**: {XXX}, {N}, {product_name}, {artifact-type}

### Artifact Path Patterns Section (lines 346-402)
**Format**: Explicit enumeration with full paths from repo root

**Subsections**:
1. Path Variables: {id}, {version}, {product_name}, {feature_name}
2. Input Artifact Paths: 12 artifact types listed explicitly
3. Template Paths: 12 template paths listed explicitly
4. Generator Paths: 12 generator paths listed explicitly

---

## Critical Issue: Variable Naming Inconsistency

| Folder Structure | Artifact Path Patterns | Meaning |
|------------------|----------------------|---------|
| `{XXX}` | `{id}` | Artifact ID (e.g., 005, 042, 123) |
| `{N}` | `{version}` | Version number (1, 2, 3) |
| `{product_name}` | `{product_name}` | ✓ Consistent |
| `{artifact-type}` | *(not used)* | Artifact type name |
| *(not defined)* | `{feature_name}` | Feature name for backlog stories |

**Problem**: Same concepts with different variable names create confusion and maintenance burden.

---

## Redundancy Analysis

### What Folder Structure Provides
✓ Visual tree hierarchy
✓ Directory organization understanding
✓ Pattern-based file naming (`{artifact-type}-template.xml`)
✓ Inline examples for clarity
✓ Single view of entire project structure

### What Artifact Path Patterns Provides
✓ Explicit full paths from repo root
✓ Complete enumeration of all 12 artifact types
✓ Guaranteed completeness (all types accounted for)
✓ Copy-paste ready paths for generators
✓ Separate sections for inputs, templates, generators

### Overlap Percentage
- **Input Artifact Paths**: ~80% overlap with Folder Structure `artifacts/` section
- **Template Paths**: ~90% overlap with Folder Structure `prompts/templates/` section
- **Generator Paths**: ~90% overlap with Folder Structure `prompts/` section

---

## Use Case Analysis

### Use Case 1: Generator Loading Template
**Current Approach (Artifact Path Patterns)**:
```
"Load PRD template from path: prompts/templates/prd-template.xml"
(Reference: Artifact Path Patterns section, Template Paths)
```

**Pattern-Based Approach (Folder Structure only)**:
```
"Load PRD template from: prompts/templates/{artifact-type}-template.xml
where artifact-type = 'prd'"
(Reference: Folder Structure section, prompts/templates/ pattern)
```

**Evaluation**:
- Explicit (current): More direct, less error-prone, easier to validate
- Pattern (proposed): More maintainable, fewer updates when adding artifact types
- **Winner**: Slight edge to explicit for generator execution reliability

---

### Use Case 2: Human Understanding Project Structure
**Folder Structure**: Clear tree view with examples
**Artifact Path Patterns**: Flat list, harder to scan

**Winner**: Folder Structure (clear visualization)

---

### Use Case 3: Adding New Artifact Type
**With Artifact Path Patterns**:
1. Add directory to Folder Structure
2. Add input path to Artifact Path Patterns → Input Artifact Paths
3. Add template path to Artifact Path Patterns → Template Paths
4. Add generator path to Artifact Path Patterns → Generator Paths
**Total**: 4 updates

**Without Artifact Path Patterns** (pattern-based):
1. Add directory to Folder Structure with pattern examples
**Total**: 1 update

**Winner**: Pattern-based approach (75% less maintenance)

---

### Use Case 4: Validation & Completeness
**With Artifact Path Patterns**:
- Explicit enumeration ensures all 12 types accounted for
- Easy to scan and verify completeness
- Can count: "Do we have 12 input paths? 12 template paths? 12 generator paths?"

**Without Artifact Path Patterns**:
- Must derive completeness from Folder Structure patterns
- Harder to verify all types have corresponding templates/generators
- More prone to missing artifact types

**Winner**: Artifact Path Patterns (explicit validation checklist)

---

### Use Case 5: Generator Prompt Token Efficiency
**Artifact Path Patterns in generator context** (~350 tokens):
- 4 subsections with explicit lists
- 12 × 3 = 36 explicit path entries

**Folder Structure in generator context** (~200 tokens):
- Tree structure with patterns
- Generators construct paths from patterns

**Winner**: Folder Structure (43% fewer tokens in generator prompts)

---

## Value Assessment Summary

| Subsection | Redundancy | Unique Value | Keep? |
|------------|-----------|--------------|-------|
| **Path Variables** | HIGH (duplicates Folder Structure vars) | None (inconsistent naming) | ❌ REMOVE |
| **Input Artifact Paths** | HIGH (~80% overlap) | Explicit enumeration for validation | 🟡 QUESTIONABLE |
| **Template Paths** | VERY HIGH (~90% overlap) | Explicit enumeration, easier generator reference | 🟡 QUESTIONABLE |
| **Generator Paths** | VERY HIGH (~90% overlap) | Explicit enumeration, easier generator reference | 🟡 QUESTIONABLE |

---

## Recommendations

### Option A: Remove Artifact Path Patterns Entirely (Aggressive)
**Changes**:
1. Delete entire "Artifact Path Patterns" section
2. Update generator prompts to reference Folder Structure patterns
3. Generators construct paths: `prompts/templates/{artifact-type}-template.xml`

**Pros**:
- Zero redundancy
- Single source of truth (Folder Structure)
- Easier maintenance (1 location for updates)
- Fewer tokens in generator prompts

**Cons**:
- Lose explicit validation checklist
- Generators must construct paths (slightly more error-prone)
- Less direct copy-paste reference for generators

**Risk**: Medium (requires generator prompt updates, testing)

---

### Option B: Simplify to Validation Checklist Only (Moderate)
**Changes**:
1. Remove "Path Variables" (use Folder Structure variables)
2. Consolidate all paths into single validation checklist:

```markdown
**Artifact Path Validation Checklist**:

All paths follow patterns defined in "Folder Structure" section.

**12 Artifact Types** (verify completeness):
- [x] Business Research: artifacts/research/, prompts/templates/business-research-template.md, prompts/business-research-generator.xml
- [x] Implementation Research: artifacts/research/, prompts/templates/implementation-research-template.md, prompts/implementation-research-generator.xml
- [x] Product Vision: artifacts/product_visions/, prompts/templates/product-vision-template.xml, prompts/product-vision-generator.xml
[... 9 more entries ...]

**Usage**: Generators reference Folder Structure patterns and construct paths as needed.
```

**Pros**:
- Preserves validation value (completeness checking)
- Reduces redundancy by ~70%
- Single table format easier to scan
- Still allows pattern-based path construction

**Cons**:
- Still some redundancy (but much less)
- Requires generator prompt updates

**Risk**: Low (smaller change, preserves validation)

---

### Option C: Keep Current Structure, Fix Inconsistencies (Conservative)
**Changes**:
1. Standardize variable naming: Use {id} and {version} everywhere (or {XXX} and {N} everywhere)
2. Add clearer note: "This section provides explicit enumeration for validation. See Folder Structure for patterns."
3. No structural changes

**Pros**:
- No generator prompt changes needed
- Preserves all current functionality
- Fixes critical naming inconsistency

**Cons**:
- Maintains high redundancy (~80%)
- Continued maintenance burden

**Risk**: Minimal (no structural changes)

---

## Final Recommendation

**Recommended**: **Option B - Simplify to Validation Checklist**

**Rationale**:
1. **Eliminates redundancy**: Reduces from 3 separate lists to 1 compact table
2. **Preserves validation value**: Explicit enumeration ensures all 12 artifact types covered
3. **Improves maintainability**: Single table format easier to update when adding artifact types
4. **Reduces token usage**: ~70% reduction in this section's size
5. **Low risk**: Smaller change than Option A, preserves core validation function

**Implementation**:
- Phase 1: Create consolidated validation checklist table
- Phase 2: Update generator prompts to reference Folder Structure patterns
- Phase 3: Remove redundant Path Variables, Input/Template/Generator Path sections
- Phase 4: Test all 12 generators with updated paths

---

## Next Steps

1. Review recommendation with stakeholders
2. Choose option (A, B, or C)
3. Create implementation task if Option A or B selected
4. Fix variable naming inconsistency regardless of option chosen

---

## Implementation Summary

**Decision**: **Option A - Remove Artifact Path Patterns Entirely**
**Date**: 2025-10-13
**Status**: CLAUDE.md Updated - Generator Updates Pending

### Changes Completed
1. ✅ Deleted entire "Artifact Path Patterns" section from CLAUDE.md (previously lines 346-402)
2. ✅ Updated "SDLC Artifact Dependency Flow" section header to reference "Folder Structure" instead of deleted section
3. ✅ "Folder Structure" now sole source of truth for paths and naming conventions

### Remaining Work (Manual)
- ⏳ Update all 12 generator prompts to reference "Folder Structure" patterns
- ⏳ Generators should construct paths from patterns:
  - Templates: `prompts/templates/{artifact-type}-template.xml`
  - Artifacts: `artifacts/{directory}/{PREFIX}-{id}_{artifact}_v{version}.md`
- ⏳ Test all 12 generators to ensure path construction works correctly

### Impact
- **Redundancy eliminated**: 100% (entire redundant section removed)
- **Maintenance improvement**: Path changes now require editing 1 location only (Folder Structure)
- **Token savings**: ~350 tokens removed from CLAUDE.md
- **Single source of truth**: Folder Structure is now definitive reference

---

**Document Owner**: Context Engineering PoC Team
**Status**: Implementation Complete (CLAUDE.md) - Generator Updates Required

# Metadata Standards Quick Reference
**Version:** 1.0 | **Date:** 2025-10-11

---

## Artifact ID Prefixes

| Artifact | Prefix | Example | Pattern |
|----------|--------|---------|---------|
| Product Vision | **VIS** | VIS-001 | VIS-XXX |
| Initiative | INIT | INIT-042 | INIT-XXX |
| Epic | EPIC | EPIC-123 | EPIC-XXX |
| PRD | PRD | PRD-005 | PRD-XXX |
| High-Level Story | HLS | HLS-078 | HLS-XXX |
| Backlog Story | US | US-234 | US-XXX |
| Spike | SPIKE | SPIKE-042 | SPIKE-XXX |
| ADR | ADR | ADR-008 | ADR-XXX |
| Tech Spec | **SPEC** | SPEC-015 | SPEC-XXX |
| Implementation Task | TASK | TASK-567 | TASK-XXX |

**Bold** = New or changed

---

## Status Values by Artifact Type

### Research (Business, Implementation)
- `Draft` → `In Review` → `Finalized`

### Strategic (Vision, Initiative, Epic)
- `Draft` → `In Review` → `Approved` → `Active`/`Planned`/`In Progress` → `Completed`
- Initiative also: `Cancelled`

### Requirements (PRD, High-Level Story)
- `Draft` → `In Review` → `Approved` → `Ready` → `In Progress` → `Completed`

### Implementation (Backlog Story, Task)
- `Backlog` → `Ready` → `To Do` → `In Progress` → `In Review` → `Done`

### Spike
- `Planned` → `In Progress` → `Completed`

### Architecture (ADR, Tech Spec)
- `Proposed` → `Accepted` → `Active` → `Deprecated`/`Superseded`

---

## Field Naming Conventions

### Parent Links (Direct Hierarchical)
```yaml
Parent Product Vision: VIS-XXX
Parent Initiative: INIT-XXX
Parent Epic: EPIC-XXX
Parent PRD: PRD-XXX
Parent Story ID: US-XXX
```

### Related Links (Cross-References)
```yaml
Related PRD: [Link]
Related ADR: [Link]
Related Tech Spec: [Link]
```

### Research Links
```yaml
Informed By Business Research: [Link]
Informed By Implementation Research: [Link]
Informed By Spike: SPIKE-XXX
```

---

## Traceability Matrix (Parent → Child)

```
Business Research ─┬─→ Product Vision ─┬─→ Initiative ──→ Epic
                   │                   │
                   │                   └─→ Epic
                   │
                   └─→ Epic ──→ PRD ─┬─→ High-Level Story ──→ Backlog Story
                                     │
                                     └─→ Backlog Story

Implementation Research ──→ Backlog Story ─┬─→ Spike ─┬─→ ADR ──→ Tech Spec ──→ Task
                                            │          │
                                            ├─→ ADR ───┤
                                            │          │
                                            ├─→ Tech Spec
                                            │
                                            └─→ Task
```

---

## Required Metadata Fields by Artifact

### Product Vision
```yaml
## Metadata
- Vision ID: VIS-XXX  [NEW]
- Informed By Business Research: [Link]  [NEW]

## Business Research References [NEW SECTION]
## Downstream Artifacts [NEW SECTION]
  - Initiatives (table)
  - Epics (table)
```

### Initiative
```yaml
## Metadata
- Parent Product Vision: VIS-XXX  [NEW]
- Informed By Business Research: [Link]  [NEW]

## Vision Alignment [NEW SECTION]
## Business Research References [NEW SECTION]
```

### Epic
```yaml
## Metadata
- Parent Product Vision: VIS-XXX  [RENAMED from "Product Vision"]
- Parent Initiative: INIT-XXX (if applicable)  [NEW]
- Informed By Business Research: [Link]  [NEW]

## Parent Artifact Context [NEW SECTION]
## Business Research References [NEW SECTION]
## Downstream Artifacts [NEW SECTION]
  - PRDs (table)
  - High-Level Stories (table)
```

### PRD
```yaml
## Metadata
- Parent Epic: EPIC-XXX  [NEW]
- Informed By Business Research: [Link - optional]  [NEW]
- Informed By Implementation Research: [Link - optional]  [NEW]

## Parent Artifact Context [NEW SECTION]
## Research References [NEW SECTION]
## Downstream Artifacts [NEW SECTION]
  - High-Level Stories (table)
  - Backlog Stories (table)
  - FR Coverage table
```

### High-Level Story
```yaml
## Metadata
- Parent Epic: [EPIC-XXX]  [KEEP]
- Parent PRD: [PRD-XXX]  [NEW]
- PRD Section: [Section X.Y]  [NEW]
- Functional Requirements: [FR-01, FR-02]  [NEW]

## Parent Artifact Context [NEW SECTION]
```

### Backlog Story
```yaml
## Related PRD → Rename to:
## Parent PRD Details
- Parent PRD: PRD-XXX  [RENAMED from "Related PRD"]
- Parent High-Level Story: HLS-XXX  [RENAMED from "High-Level Story"]
- Informed By Implementation Research: [Link]  [NEW]

## Implementation Research References [NEW SECTION]
```

### Spike
```yaml
## Metadata
- Parent: [US-XXX or SPEC-XXX]  [KEEP]

## Traceability [NEW SECTION]
  - Triggered By: US-XXX or SPEC-XXX
  - Informs: ADR/Tech Spec/Backlog Story
```

### ADR
```yaml
## Metadata
- Parent Story ID: US-XXX  [RENAMED from "Story ID"]
- Informed By Spike: SPIKE-XXX (if applicable)  [NEW]
- Informed By Implementation Research: [Link]  [NEW]

## Research & Investigation Context [NEW SECTION]
```

### Tech Spec
```yaml
## Metadata
- Spec ID: SPEC-XXX  [RENAMED from "TECH-SPEC-XXX"]
- Parent Story ID: US-XXX  [RENAMED from "Story ID"]
- Related PRD: [Link]  [KEEP]
- Related ADR: [Link]  [KEEP]
- Informed By Spike: SPIKE-XXX (if applicable)  [NEW]
- Informed By Implementation Research: [Link]  [NEW]

## Research & Investigation Context [NEW SECTION]
```

### Implementation Task
```yaml
## Metadata
- Parent Story ID: US-XXX  [RENAMED from "Story ID"]

## Implementation Research Reference [ENHANCED]
  - Add Primary Research link
  - Add specific §X.Y references
```

---

## Research Integration Patterns

### Business Research → Strategic Artifacts

**Informs:**
- Product Vision (market positioning, personas, metrics)
- Initiative (strategic justification, market opportunity)
- Epic (market gaps, capabilities, user needs)
- PRD (optional - market context)
- High-Level Story (optional - persona details)

**Reference Format:**
```markdown
## Business Research References
**Primary Research:** [Link]

**Applied Insights:**
- §[X.Y] [Section]: [How applies]
```

### Implementation Research → Technical Artifacts

**Informs:**
- PRD (optional - technical feasibility, NFRs)
- Backlog Story (patterns, architecture context)
- Spike (investigation baseline)
- ADR (architecture patterns, comparisons)
- Tech Spec (implementation patterns, code examples)
- Implementation Task (detailed code examples)

**Reference Format:**
```markdown
## Implementation Research References
**Primary Research:** [Link]

**Technical Patterns Applied:**
- §[X.Y] [Pattern]: [How applies]
  - Code Example: [Reference]
```

---

## Validation Checklist (All Artifacts)

**Upstream Traceability:**
- [ ] Parent fields populated with valid IDs
- [ ] Parent artifact status is approved/finalized
- [ ] Informed By fields populated (if applicable)
- [ ] Section references (§X.Y) are valid

**Downstream Traceability (Strategic Artifacts):**
- [ ] Downstream Artifacts section created
- [ ] Forward links updated in parent artifacts

**Link Validation:**
- [ ] All artifact ID links are accessible
- [ ] All research links point to finalized versions
- [ ] All section references exist in documents

**Consistency:**
- [ ] Status follows standardized values
- [ ] ID format follows prefix pattern
- [ ] Field naming follows conventions

---

## Common Patterns

### Creating New Artifact
1. Use updated template from `/prompts/templates/`
2. Fill all required metadata fields
3. Add parent artifact links
4. Add research references (if applicable)
5. Update parent's downstream tracking table
6. Run validation checklist

### Updating Existing Artifact
1. Check downstream artifacts table
2. Notify downstream artifact owners
3. Update version number
4. Add change log entry
5. Re-run validation

### Spike → ADR → Tech Spec Flow
```
1. Backlog Story: Open question [REQUIRES SPIKE]
2. Create Spike: Parent = US-XXX
3. Complete Spike: Recommendation documented
4. Create ADR: Parent = US-XXX, Informed By Spike = SPIKE-XXX
5. Create Tech Spec: Parent = US-XXX, Informed By Spike = SPIKE-XXX
6. Update Backlog Story: Reference spike findings
```

---

## Section Reference Format

**Standard Pattern:** `§[X.Y]` or `§[X.Y.Z]`

**Examples:**
- `§3.1` - Section 3, subsection 1
- `§4.2.3` - Section 4, subsection 2, sub-subsection 3
- `§Appendix A` - Appendix reference

**In Metadata:**
```markdown
**Applied Insights:**
- §3.1 Market Gap Analysis: [Description]
- §4.2 Capability Recommendation: [Description]
```

---

## Troubleshooting

### "Parent artifact not found"
→ Verify parent ID format matches standard prefix
→ Check that parent artifact file exists
→ Confirm parent artifact version is finalized/approved

### "Research reference invalid"
→ Confirm research document status is "Finalized"
→ Verify section number exists in research document
→ Check that research file path is correct

### "Inconsistent status value"
→ Use standardized status from this reference guide
→ Check artifact type to determine valid statuses
→ Update template if using old status values

### "Missing downstream links"
→ When creating child artifact, update parent's downstream table
→ Maintain bidirectional links for traceability
→ Review quarterly for orphaned artifacts

---

## Quick Decision Tree

**"Which research document do I reference?"**

```
Is artifact about business strategy, market, or users?
├─ YES → Business Research
└─ NO → Is artifact about implementation or technical approach?
    ├─ YES → Implementation Research
    └─ NO → Artifact may not need research reference
```

**"What status should this artifact have?"**

```
What type of artifact?
├─ Research → Draft/In Review/Finalized
├─ Strategy (Vision/Initiative/Epic) → Draft/.../Approved/Active/Completed
├─ Requirements (PRD/HLS) → Draft/.../Approved/Ready/In Progress/Completed
├─ Implementation (Story/Task) → Backlog/Ready/To Do/In Progress/In Review/Done
├─ Spike → Planned/In Progress/Completed
└─ Architecture (ADR/Spec) → Proposed/Accepted/Active/Deprecated/Superseded
```

**"How do I name the parent link field?"**

```
Is this the direct parent (1 level up in hierarchy)?
├─ YES → Use "Parent [Artifact]: [ID]"
└─ NO → Is it informational/cross-reference?
    ├─ YES → Use "Related [Artifact]: [Link]"
    └─ NO → Is it a research document?
        └─ YES → Use "Informed By [Research Type]: [Link]"
```

---

## Migration Priority

### Immediate (Active Work)
1. Artifacts with status "In Progress"
2. Artifacts referenced by active work

### Within 1 Week
1. Approved artifacts in current sprint/quarter
2. Artifacts referenced in near-term roadmap

### Opportunistic
1. Completed artifacts
2. Archived artifacts

---

## Tools & Resources

**Templates Location:** `/prompts/templates/`
**Examples:** Each template includes `<examples>` section
**Full Guidelines:** `docs/sdlc_artifacts_comprehensive_guideline.md`
**Traceability Analysis:** `metadata_traceability_analysis.md`
**Detailed Plan:** `metadata_refinement_plan.md`

**Validation Script (Future):** `scripts/validate_traceability.sh`

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-10-11 | Initial quick reference for metadata refinement |

---

**For Questions:** Contact Context Engineering Team
**For Issues:** Create GitHub issue with label `metadata`

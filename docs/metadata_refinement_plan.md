# Metadata Refinement Plan - SDLC Artifact Templates
**Date:** 2025-10-11
**Status:** Implementation Ready
**Based On:** Metadata Traceability Analysis v1.0

---

## Executive Summary

**Objective:** Enhance traceability across all SDLC artifact templates by adding explicit metadata fields for parent relationships, research references, and bidirectional linking.

**Scope:** 12 SDLC artifact templates requiring metadata enhancements
**Impact:** Improves traceability completeness from 45% to 90%
**Effort:** 4 weeks (phased implementation)

**Key Changes:**
1. Add explicit "Parent" fields to 6 templates (Vision, Initiative, Epic, PRD, HLS, Backlog Story)
2. Add "Informed By" research fields to 8 templates
3. Add bidirectional forward links to 5 templates
4. Standardize field naming and status values across all templates
5. Add traceability validation checklists

---

## Phase 1: Critical Upstream Links (Week 1, Days 1-2)

**Priority:** 🔴 **CRITICAL** - Establishes core parent-child hierarchy

### Changes Required

#### 1.1 Product Vision Template
**File:** `prompts/templates/product-vision-template.xml`

**Add to Metadata Section (after line 30):**

```markdown
## Metadata
- **Author:** [name]
- **Date:** [YYYY-MM-DD]
- **Version:** [version]
- **Status:** [Draft/Review/Approved]
- **Vision ID:** VIS-[XXX]  <!-- ADD NEW -->
- **Informed By Business Research:** [Link to Business Research document]  <!-- ADD NEW -->
```

**Add New Section (after Strategic Alignment):**

```markdown
## Business Research References

**Primary Research Document:** [Link to Business Research report]

**Key Insights Applied:**
- **Market Positioning (§5.1):** [How positioning recommendation informs this vision]
- **Target Users (§Appendix A):** [Which personas from research are primary focus]
- **Success Metrics (§4.1):** [Which capability recommendations inform key features]

**Market Data Supporting Vision:**
- [Data point 1 from research with section reference]
- [Data point 2 from research with section reference]
```

**Add to Related Documents Section:**

```markdown
## Related Documents
- **Business Research:** [Link to Business Research report] (NEW)
- [Links to market research, user studies, competitive analysis]

## Downstream Artifacts (Implements This Vision)

**Initiatives:**
| Initiative ID | Title | Status | Owner |
|---------------|-------|--------|-------|
| [To be populated as initiatives are created] |

**Epics:**
| Epic ID | Title | Status | Target Release |
|---------|-------|--------|----------------|
| [To be populated as epics are created] |

*Note: This section tracks what implements this vision. Update when new initiatives/epics reference this vision.*
```

**Rationale:** Product Vision is strategic root artifact and must trace back to business research that informed it.

---

#### 1.2 Initiative Template
**File:** `prompts/templates/initiative-template.xml`

**Add to Metadata Section (after line 34):**

```markdown
## Metadata
- **Initiative ID:** INIT-[XXX]
- **Status:** [Draft/Approved/In Progress/Completed/Cancelled]
- **Priority:** [Strategic/High/Medium]
- **Owner:** [Executive Sponsor Name & Title]
- **Business Unit:** [Product/Engineering/Sales/etc.]
- **Time Horizon:** [Q1-Q3 2025]
- **Budget:** $[Amount]
- **Parent Product Vision:** VIS-[XXX]  <!-- ADD NEW -->
- **Related Strategy Doc:** [Link to portfolio/business strategy]
- **Informed By Business Research:** [Link to Business Research document]  <!-- ADD NEW -->
```

**Add New Section (before Supporting Epics):**

```markdown
## Vision Alignment

**Parent Product Vision:** [VIS-XXX: Vision Title]
- **Link:** [URL to Product Vision document v3]
- **Vision Alignment:** [How this initiative directly implements the vision]

## Business Research References

**Primary Research Document:** [Link to Business Research report]

**Strategic Insights Applied:**
- **Market Opportunity (§2.1):** [Specific market segment or opportunity]
- **Competitive Positioning (§5.1):** [How this initiative supports positioning]
- **Roadmap Phase (§5.5):** [Which roadmap phase this initiative maps to]

**Business Justification:**
[Reference specific business research findings that justify investment in this initiative]
```

**Rationale:** Initiatives must trace to Product Vision and business research that justified the strategic direction.

---

#### 1.3 Epic Template
**File:** `prompts/templates/epic-template.xml`

**Modify Metadata Section (lines 26-32):**

```markdown
## Metadata
- **Epic ID:** EPIC-[XXX]
- **Status:** [Draft/Planned/In Progress/Completed]
- **Priority:** [Critical/High/Medium/Low]
- **Parent Product Vision:** VIS-[XXX]  <!-- RENAME from "Product Vision" -->
- **Parent Initiative:** INIT-[XXX] (if part of initiative)  <!-- ADD NEW -->
- **Owner:** [Name]
- **Target Release:** [Q1 2025]
- **Informed By Business Research:** [Link to Business Research document]  <!-- ADD NEW -->
```

**Add New Section (after Epic Statement):**

```markdown
## Parent Artifact Context

**Parent Product Vision:** [VIS-XXX: Vision Title]
- **Link:** [URL to Product Vision document v3]
- **Vision Capability:** [Which key capability from vision this epic implements]

**Parent Initiative:** [INIT-XXX: Initiative Title] (if applicable)
- **Link:** [URL to Initiative document]
- **Initiative Contribution:** [How this epic contributes to initiative OKRs]

## Business Research References

**Primary Research Document:** [Link to Business Research report]

**Market Insights Applied:**
- **Gap Analysis (§3.1):** [Specific gap this epic addresses]
- **Capability Recommendation (§4.1):** [Which recommended capability this implements]
- **User Persona (§Appendix A):** [Target persona from research]

**Competitive Context:**
[Reference competitive analysis from business research that justifies this epic's approach]
```

**Add to Related Documents Section:**

```markdown
## Related Documents
- **Parent Product Vision:** [VIS-XXX Link] (NEW)
- **Parent Initiative:** [INIT-XXX Link] (NEW - if applicable)
- **Business Research:** [Link with specific sections referenced] (NEW)
- Related ADRs: [Links]
- Technical Specs: [Links]
- User Research: [Links]

## Downstream Artifacts (Implements This Epic)

**PRDs:**
| PRD ID | Title | Status | Owner |
|--------|-------|--------|-------|
| [To be populated as PRDs are created] |

**High-Level Stories:**
| Story ID | Title | Status | Target Release |
|----------|-------|--------|----------------|
| [To be populated as stories are created] |

*Note: Update this section when PRDs or stories reference this epic.*
```

**Rationale:** Epic must link to both Product Vision and Initiative (when applicable), plus business research.

---

#### 1.4 PRD Template
**File:** `prompts/templates/prd-template.xml`

**Modify Metadata Section (lines 25-30):**

```markdown
## Metadata
- **PRD ID:** PRD-[XXX]
- **Author:** [name]
- **Date:** [date]
- **Version:** [version]
- **Status:** [Draft/Review/Approved]
- **Parent Epic:** EPIC-[XXX]  <!-- ADD NEW -->
- **Informed By Business Research:** [Link - optional for market context]  <!-- ADD NEW -->
- **Informed By Implementation Research:** [Link - optional for technical feasibility]  <!-- ADD NEW -->
```

**Add New Section (after Metadata, before Executive Summary):**

```markdown
## Parent Artifact Context

**Parent Epic:** [EPIC-XXX: Epic Title]
- **Link:** [URL to Epic document v3]
- **Epic Scope Coverage:** [Which portion of the epic this PRD addresses]
- **Epic Acceptance Criteria Mapping:** [Which epic-level criteria this PRD satisfies]

## Research References

### Business Research (Optional - When Market Context Needed)
**Document:** [Link to Business Research report]

**Applied Insights:**
- **§[X.Y]: [Section Title]:** [Insight relevant to PRD requirements]
- **§[X.Y]: [Section Title]:** [Market data supporting business case]

*Use when PRD requires market validation, competitive positioning, or business model context.*

### Implementation Research (Optional - When Technical Feasibility Needed)
**Document:** [Link to Implementation Research report]

**Applied Insights:**
- **§[X.Y]: [Section Title]:** [Technical feasibility insight]
- **§[X.Y]: [Section Title]:** [Architecture pattern or constraint]

*Use when PRD includes NFRs, technical constraints, or architecture considerations requiring research validation.*

**Note:** PRD is a bridge artifact. Business Research is typically consumed at Epic level, and Implementation Research at Backlog Story level. Only reference research here when needed to inform requirements definition.
```

**Add to End of Document:**

```markdown
## Downstream Artifacts (Implements This PRD)

**High-Level Stories:**
| Story ID | Title | Status | Target Release |
|----------|-------|--------|----------------|
| [To be populated as stories are created] |

**Backlog Stories:**
| Story ID | Title | Status | Sprint |
|----------|-------|--------|--------|
| [To be populated as backlog stories are created] |

*Note: Update this section as stories reference this PRD.*

## Related Documents
- **Parent Epic:** [EPIC-XXX Link]
- **Business Research:** [Link - if referenced]
- **Implementation Research:** [Link - if referenced]
```

**Rationale:** PRD must explicitly link to parent Epic and optionally to research when needed as bridge artifact.

---

#### 1.5 High-Level User Story Template
**File:** `prompts/templates/high-level-user-story-template.xml`

**Modify Metadata Section (lines 28-35):**

```markdown
## Metadata
- **Story ID:** HLS-[XXX]
- **Status:** [Draft/Ready/In Progress/Completed]
- **Priority:** [Critical/High/Medium/Low]
- **Parent Epic:** [EPIC-XXX]  <!-- KEEP -->
- **Parent PRD:** [PRD-XXX]  <!-- ADD NEW -->
- **PRD Section:** [Section X.Y - specific section this story addresses]  <!-- ADD NEW -->
- **Functional Requirements:** [FR-01, FR-02, FR-03]  <!-- ADD NEW - from PRD -->
- **Owner:** [Product Owner Name]
- **Target Release:** [Q1 2025 / Sprint 15-17]
```

**Add New Section (after User Story Statement):**

```markdown
## Parent Artifact Context

**Parent Epic:** [EPIC-XXX: Epic Title]
- **Link:** [URL to Epic document v3]
- **Epic Contribution:** [How this story contributes to epic completion]

**Parent PRD:** [PRD-XXX: PRD Title]
- **Link:** [URL to PRD document v3]
- **PRD Section:** [Section X.Y that defines this story]
- **Functional Requirements Coverage:**
  - **FR-01:** [Requirement description from PRD]
  - **FR-02:** [Requirement description from PRD]
  - **FR-03:** [Requirement description from PRD]

**User Persona Source:** [Business Research Appendix A - Persona Name]
```

**Rationale:** High-Level Story decomposes from PRD, so must explicitly link to both Epic and PRD with FR mapping.

---

#### 1.6 Backlog Story Template
**File:** `prompts/templates/backlog-story-template.xml`

**Modify Related PRD Section (lines 40-44):**

```markdown
## Related PRD
**PRD ID:** [PRD-XXX]
**Parent PRD Link:** [URL to PRD document v3]  <!-- ADD NEW -->
**Parent High-Level Story:** [HLS-XX reference from PRD or standalone]  <!-- RENAME from "High-Level Story" -->
**Functional Requirements Covered:** [FR-01, FR-03, ...]
**Informed By Implementation Research:** [Link to Implementation Research document]  <!-- ADD NEW -->
```

**Add New Section (after Related PRD):**

```markdown
## Implementation Research References

**Primary Research Document:** [Link to Implementation Research report]

**Technical Patterns Applied:**
- **§[X.Y]: [Pattern Name]:** [How this pattern applies to implementation]
  - **Example Code:** [Reference to research code example if applicable]
- **§[X.Y]: [Security Pattern]:** [Security implementation guidance]
- **§[X.Y]: [Testing Strategy]:** [Testing approach from research]

**Anti-Patterns Avoided:**
- **§[X.Y]: [Pitfall Name]:** [How we're avoiding this pitfall]

**Performance Considerations:**
- **§[X.Y]: [Performance Pattern]:** [Target metrics and approach]

*Implementation tasks (in TODO.md) should reference specific research sections for detailed guidance.*
```

**Rationale:** Backlog Story is where Implementation Research is primarily consumed. Explicit linkage is critical.

---

## Phase 2: Research Integration (Week 1, Days 3-5)

**Priority:** 🟠 **HIGH** - Completes research artifact integration

### Changes Required

#### 2.1 ADR Template
**File:** `prompts/templates/adr-template.xml`

**Modify Metadata Section (lines 21-26):**

```markdown
## Metadata
- **Date:** [YYYY-MM-DD]
- **Status:** [Proposed | Accepted | Deprecated | Superseded]
- **Deciders:** [Names]
- **Parent Story ID:** US-[XXX]  <!-- RENAME from "Story ID" -->
- **Informed By Spike:** SPIKE-[XXX] (if spike provided evidence)  <!-- ADD NEW -->
- **Informed By Implementation Research:** [Link to Implementation Research document]  <!-- ADD NEW -->
```

**Add New Section (after Context):**

```markdown
## Research & Investigation Context

**Parent Backlog Story:** [US-XXX: Story Title]
- **Link:** [URL to Backlog Story]
- **Decision Driver:** [Why this decision was needed for the story]

**Informed By Spike:** [SPIKE-XXX: Spike Title] (if applicable)
- **Link:** [URL to Spike document]
- **Key Findings:** [Summary of spike findings that informed this decision]
- **Evidence Applied:** [Benchmarks, prototypes, or data from spike]

**Implementation Research References:**
**Primary Research Document:** [Link to Implementation Research report]

**Relevant Patterns:**
- **§[X.Y]: [Architecture Pattern]:** [How this pattern informs the decision]
- **§[X.Y]: [Technology Stack]:** [Technology comparison from research]

**Pitfalls Considered:**
- **§[X.Y]: [Anti-Pattern]:** [Why alternatives were rejected based on research]
```

**Rationale:** ADR often follows spike investigation and should reference Implementation Research for context.

---

#### 2.2 Tech Spec Template
**File:** `prompts/templates/tech-spec-template.xml`

**Modify Metadata Section (lines 20-34):**

```markdown
## Metadata
- **TechSpec ID:** SPEC-[XXX]  <!-- RENAME from TECH-SPEC-XXX -->
- **Date:** [YYYY-MM-DD]
- **Status:** [Proposed | Accepted | Deprecated | Superseded]
- **Deciders:** [Names]
- **Parent Story ID:** US-[XXX]  <!-- RENAME from "Story ID" -->
- **Related PRD:** [Link]  <!-- KEEP -->
- **Related ADR:** [Link]  <!-- KEEP -->
- **Informed By Spike:** SPIKE-[XXX] (if spike provided implementation guidance)  <!-- ADD NEW -->
- **Informed By Implementation Research:** [Link to Implementation Research document]  <!-- ADD NEW -->

## Overview
**Summary:** [One paragraph overview]
**Related PRD:** [Link]
**Related ADR:** [Link]
```

**Add New Section (after Overview):**

```markdown
## Research & Investigation Context

**Parent Backlog Story:** [US-XXX: Story Title]
- **Link:** [URL to Backlog Story]

**Informed By Spike:** [SPIKE-XXX: Spike Title] (if applicable)
- **Link:** [URL to Spike document]
- **Implementation Guidance:** [How spike findings shaped this technical spec]
- **Key Decisions:** [Decisions made based on spike evidence]

**Implementation Research References:**
**Primary Research Document:** [Link to Implementation Research report]

**Implementation Patterns Applied:**
- **§[X.Y]: [Technical Capability]:** [Detailed implementation pattern]
  - **Code Example Reference:** [Link to Appendix B example if applicable]
- **§[X.Y]: [Security Implementation]:** [Security pattern applied]
- **§[X.Y]: [Testing Strategy]:** [Testing approach from research]

**Performance Targets:**
- **§[X.Y]: [Performance Benchmarks]:** [Target metrics from research]

**Observability:**
- **§[X.Y]: [Monitoring Implementation]:** [Logging and metrics approach]
```

**Rationale:** Tech Spec is implementation-level artifact requiring extensive Implementation Research references.

---

#### 2.3 Implementation Task Template
**File:** `prompts/templates/implementation-task-template.xml`

**Modify Implementation Research Reference Section (lines 119-122):**

```markdown
### Implementation Research Reference
[If applicable, reference Implementation Research sections]
- **Primary Research:** [Link to Implementation Research document]  <!-- ADD NEW -->
- **§[X.Y] - [Pattern Name]:** [Specific guidance from research]
- **§[X.Y] - [Anti-Pattern]:** [Pitfall to avoid with explanation]
- **Code Example:** [Link to Appendix B example if applicable]

**Relevant Patterns for This Task:**
- **§[X.Y]: [Specific Pattern]:** [How to apply in this task]
- **§[X.Y]: [Testing Pattern]:** [Test strategy for this task]

**Reference Implementation:**
[Link to similar existing code in codebase OR research code example]
```

**Rationale:** Implementation Task already has research references, but they need strengthening and standardization.

---

## Phase 3: Bidirectional Forward Links (Week 2)

**Priority:** 🟡 **MEDIUM** - Enables forward traceability and impact analysis

### Changes Required

#### 3.1 Business Research Template
**File:** `prompts/templates/business_research_template.xml`

**Add New Section (after Conclusion, before Appendices):**

```markdown
---

## Traceability: Downstream Artifacts

**This business research document informs the following SDLC artifacts.**

*Note: This section should be maintained as downstream artifacts reference this research. Use document ID and section references to track which insights are applied where.*

### Product Vision
- **[VIS-XXX: Vision Title]**
  - Referenced Sections: §1.1, §3.1, §5.1
  - Key Insights Applied: [Brief description]

### Initiatives
- **[INIT-XXX: Initiative Title]**
  - Referenced Sections: §2.1, §5.4
  - Key Insights Applied: [Brief description]

### Epics
- **[EPIC-XXX: Epic Title]**
  - Referenced Sections: §3.1, §4.1
  - Key Insights Applied: [Brief description]

### PRDs (Optional References)
- **[PRD-XXX: PRD Title]**
  - Referenced Sections: §2.3, §5.2
  - Key Insights Applied: [Brief description]

### High-Level Stories (Optional References)
- **[HLS-XXX: Story Title]**
  - Referenced Sections: §Appendix A (Persona)
  - Key Insights Applied: [Brief description]

**Maintenance Note:** This section enables impact analysis. When business research is updated, this list identifies which downstream artifacts may need review. Update this section when new artifacts reference this research.
```

**Rationale:** Business Research is root artifact and needs forward visibility into what it informs.

---

#### 3.2 Implementation Research Template
**File:** `prompts/templates/implementation_research_template.xml`

**Add New Section (after Technical Summary & Conclusion, before Appendices):**

```markdown
---

## Traceability: Downstream Artifacts

**This implementation research document informs the following SDLC artifacts.**

*Note: Track which technical patterns, code examples, and recommendations are applied in implementation artifacts. Update as new artifacts reference this research.*

### PRDs (Optional References - Technical Feasibility)
- **[PRD-XXX: PRD Title]**
  - Referenced Sections: §5.1 (Architecture), §5.2 (NFRs)
  - Technical Insights Applied: [Brief description]

### Backlog Stories
- **[US-XXX: Story Title]**
  - Referenced Sections: §4.1, §6.3, Appendix B
  - Patterns Applied: [Brief description]

### Spikes
- **[SPIKE-XXX: Spike Title]**
  - Referenced Sections: §2.2, §4.3
  - Investigation Baseline: [Brief description]

### ADRs (Architecture Decision Records)
- **[ADR-XXX: Decision Title]**
  - Referenced Sections: §5.1, §6.1
  - Context Provided: [Brief description]

### Technical Specifications
- **[SPEC-XXX: Spec Title]**
  - Referenced Sections: §4.1-4.7, Appendix B
  - Implementation Patterns Applied: [Brief description]

### Implementation Tasks
- **[TASK-XXX: Task Title]**
  - Referenced Sections: §4.X, Appendix B Example [N]
  - Code Examples Applied: [Brief description]

**Maintenance Note:** When implementation research is updated (new patterns, revised benchmarks), this list identifies which artifacts may need updates. Keep this section current as implementation artifacts reference research sections.
```

**Rationale:** Implementation Research needs forward visibility for change impact analysis.

---

#### 3.3 Product Vision Template
**Enhancement to Section Added in Phase 1:**

```markdown
## Downstream Artifacts (Implements This Vision)

**Note:** Maintain this section as initiatives and epics are created. Enables impact analysis when vision evolves.

### Initiatives
| Initiative ID | Title | Status | Owner | Key Results Targeted |
|---------------|-------|--------|-------|----------------------|
| INIT-001 | [Title] | [Status] | [Owner] | [Which vision capability] |
| INIT-002 | [Title] | [Status] | [Owner] | [Which vision capability] |

### Epics (Direct References)
| Epic ID | Title | Status | Target Release | Vision Capability Implemented |
|---------|-------|--------|----------------|-------------------------------|
| EPIC-001 | [Title] | [Status] | Q1 2025 | [Which key capability] |
| EPIC-002 | [Title] | [Status] | Q2 2025 | [Which key capability] |

**Vision Coverage Analysis:**
- **Key Capability 1:** Implemented by EPIC-001, EPIC-004
- **Key Capability 2:** Implemented by INIT-001 (via EPIC-002, EPIC-003)
- **Key Capability 3:** Planned - EPIC-009 (Q3 2025)

**Maintenance Schedule:** Review quarterly during roadmap planning to ensure vision coverage is complete.
```

**Rationale:** Product Vision needs to track coverage of key capabilities across initiatives/epics.

---

#### 3.4 Epic Template
**Enhancement to Section Added in Phase 1:**

```markdown
## Downstream Artifacts (Implements This Epic)

**Note:** Maintain as PRDs and stories are created. Enables epic completion tracking and impact analysis.

### PRDs
| PRD ID | Title | Status | Owner | Epic Coverage |
|--------|-------|--------|-------|---------------|
| PRD-001 | [Title] | [Status] | [Owner] | [Which epic scope] |

### High-Level Stories
| Story ID | Title | Status | Target Release | Sprint Estimate |
|----------|-------|--------|----------------|-----------------|
| HLS-001 | [Title] | [Status] | Q1 2025 | 2-3 sprints |
| HLS-002 | [Title] | [Status] | Q1 2025 | 3-4 sprints |

**Epic Completion Tracking:**
- **Total High-Level Stories:** [N]
- **Completed Stories:** [X]
- **In Progress Stories:** [Y]
- **Remaining Stories:** [Z]
- **Epic Progress:** [X/N * 100]%

**Maintenance:** Update when new PRDs/stories reference this epic, and when story status changes.
```

**Rationale:** Epic needs to track all implementing PRDs and stories for completion tracking.

---

#### 3.5 PRD Template
**Enhancement to Section Added in Phase 1:**

```markdown
## Downstream Artifacts (Implements This PRD)

**Note:** Track stories that implement this PRD's functional requirements. Update as stories are created and completed.

### High-Level Stories
| Story ID | Title | Status | FRs Covered | Target Release |
|----------|-------|--------|-------------|----------------|
| HLS-001 | [Title] | [Status] | FR-01, FR-02 | Q1 2025 |

### Backlog Stories (Detailed Implementation)
| Story ID | Title | Status | FRs Covered | Sprint | Story Points |
|----------|-------|--------|-------------|--------|--------------|
| US-001 | [Title] | [Status] | FR-01 | Sprint 12 | 5 |
| US-002 | [Title] | [Status] | FR-02 | Sprint 13 | 8 |

**Functional Requirements Coverage:**
| FR ID | Requirement | Implementing Stories | Status |
|-------|-------------|----------------------|--------|
| FR-01 | [Requirement] | US-001, US-003 | In Progress |
| FR-02 | [Requirement] | US-002 | Completed |
| FR-03 | [Requirement] | US-004, US-005 | Backlog |

**PRD Completion Tracking:**
- **Total FRs:** [N]
- **Completed FRs:** [X]
- **In Progress FRs:** [Y]
- **Remaining FRs:** [Z]
- **PRD Progress:** [X/N * 100]%

**Maintenance:** Update when stories reference PRD FRs, and track FR coverage to ensure no gaps.
```

**Rationale:** PRD needs to track FR coverage across all implementing stories to ensure requirements completeness.

---

## Phase 4: Standardization (Week 3)

**Priority:** 🟡 **MEDIUM** - Improves consistency and usability

### 4.1 Status Value Standardization

**Apply Unified Status Values to Each Template:**

| Template | Old Values | New Standardized Values | Lines to Update |
|----------|-----------|------------------------|-----------------|
| **Business Research** | Draft, Review, Final | Draft, In Review, **Finalized** | Line ~27 |
| **Implementation Research** | Draft, Review, Final | Draft, In Review, **Finalized** | Line ~27 |
| **Product Vision** | Draft, Review, Approved | Draft, In Review, **Approved** | Line ~29 |
| **Initiative** | Draft, Approved, In Progress, Completed, Cancelled | Draft, In Review, **Approved**, Active, **Completed**, **Cancelled** | Line ~28 |
| **Epic** | Draft, Planned, In Progress, Completed | Draft, In Review, **Approved**, **Planned**, In Progress, **Completed** | Line ~28 |
| **PRD** | Draft, Review, Approved | Draft, In Review, **Approved** | Line ~29 |
| **High-Level Story** | Draft, Ready, In Progress, Completed | Draft, In Review, **Approved**, **Ready**, In Progress, **Completed** | Line ~30 |
| **Backlog Story** | (undefined) | **Backlog**, **Ready**, In Progress, **In Review**, **Done** | Add to line ~30 |
| **Spike** | Not Started, In Progress, Complete | **Planned**, In Progress, **Completed** | Line ~29 |
| **ADR** | Proposed, Accepted, Deprecated, Superseded | **Proposed**, **Accepted**, Active, **Deprecated**, **Superseded** | Line ~24 |
| **Tech Spec** | Proposed, Accepted, Deprecated, Superseded | **Proposed**, **Accepted**, Active, **Deprecated**, **Superseded** | Line ~25 |
| **Implementation Task** | To Do, In Progress, In Review, Done | **To Do**, In Progress, **In Review**, **Done** | Line ~31 |

**Implementation:**
- Update `<guideline>` sections with new status values
- Update examples in `<examples>` sections
- Add status definitions in instructions if helpful

---

### 4.2 Parent Field Naming Standardization

**Apply Consistent "Parent" vs "Related" Naming:**

| Template | Current Field Name | Standardized Field Name | Change Type |
|----------|-------------------|------------------------|-------------|
| **Epic** | `Product Vision: [Link]` | `Parent Product Vision: VIS-[XXX]` | RENAME |
| **High-Level Story** | `Parent Epic: [EPIC-XXX]` | ✅ **Keep as is** | NO CHANGE |
| **Backlog Story** | `Related PRD: [PRD-XXX]` | `Parent PRD: [PRD-XXX]` | RENAME |
| **ADR** | `Story ID: US-[XXX]` | `Parent Story ID: US-[XXX]` | RENAME |
| **Tech Spec** | `Story ID: US-[XXX]` | `Parent Story ID: US-[XXX]` | RENAME |
| **Tech Spec** | `Related PRD: [Link]` | ✅ **Keep as is** (not direct parent) | NO CHANGE |
| **Tech Spec** | `Related ADR: [Link]` | ✅ **Keep as is** (not direct parent) | NO CHANGE |
| **Implementation Task** | `Story ID: US-[XXX]` | `Parent Story ID: US-[XXX]` | RENAME |

**Naming Convention Standard:**
- **"Parent [Artifact]"** - For direct parent-child hierarchical relationships (1 level up)
- **"Related [Artifact]"** - For cross-references or informational links (not direct parent)
- **"Informed By [Research]"** - For research artifact references

---

### 4.3 ID Prefix Standardization

**Update ID Prefixes:**

| Template | Current ID Format | Standardized ID Format | Change Required |
|----------|------------------|------------------------|-----------------|
| **Product Vision** | (none) | `VIS-XXX` | ADD |
| **ADR** | `ADR-[NUMBER]` | `ADR-XXX` | CHANGE label |
| **Tech Spec** | `TECH-SPEC-[XXX]` | `SPEC-XXX` | CHANGE prefix |
| **Backlog Story** | `US-[xxx]` | `US-XXX` | CHANGE to uppercase |

**Implementation:**
1. **Product Vision:** Add new `Vision ID: VIS-XXX` field to metadata
2. **ADR:** Change `ADR Number:` label to `ADR ID:` (format unchanged)
3. **Tech Spec:** Change `TechSpec ID: TECH-SPEC-XXX` to `Spec ID: SPEC-XXX`
4. **Backlog Story:** Update examples from `US-[xxx]` to `US-XXX`

---

## Phase 5: Validation & Documentation (Week 4)

**Priority:** 🟢 **LOW** - Ensures adherence and enables tooling

### 5.1 Add Traceability Validation Checklists

**Add to Every Template's "Definition of Done" Section:**

```markdown
## Traceability Validation Checklist

**Upstream Traceability:**
- [ ] All "Parent [Artifact]" fields populated with valid artifact IDs
- [ ] Parent artifact version confirmed as current (not outdated draft)
- [ ] All "Informed By" research fields populated (if applicable to artifact phase)
- [ ] Research section references are valid (§X.Y format with correct sections)

**Downstream Traceability (if applicable):**
- [ ] "Downstream Artifacts" section created (for strategic artifacts)
- [ ] Forward links updated in parent artifacts (added this artifact to parent's downstream list)

**Link Validation:**
- [ ] All artifact ID links are valid and accessible
- [ ] All research document links are valid and point to finalized versions
- [ ] All section references (§X.Y) exist in referenced documents

**Consistency Checks:**
- [ ] Status value follows standardized values for this artifact type
- [ ] ID format follows standard prefix pattern (e.g., EPIC-XXX, not epic-123)
- [ ] Field naming follows "Parent" vs "Related" conventions

**Impact Analysis:**
- [ ] If parent artifact has been updated since this artifact was created, review for impacts
- [ ] If this is an update to an existing artifact, identify affected downstream artifacts
```

---

### 5.2 Update SDLC Artifacts Comprehensive Guideline

**File:** `docs/sdlc_artifacts_comprehensive_guideline.md`

**Add New Section (Section 1.7):**

```markdown
## 1.7 Metadata Standards and Traceability

### 1.7.1 Core Metadata Fields

All SDLC artifacts include standardized metadata fields to enable traceability and impact analysis.

**Required Fields (All Artifacts):**
- **[Artifact] ID:** Unique identifier with standardized prefix
- **Status:** Standardized status value for artifact type
- **Version:** Version number (vX for documents, X.Y for templates)
- **Date:** Creation or last update date (YYYY-MM-DD)
- **Owner/Author:** Responsible individual

**Traceability Fields:**
- **Parent [Artifact]:** Direct hierarchical parent (1 level up)
- **Informed By [Research]:** Research document that informed this artifact
- **Related [Artifact]:** Cross-references to peer or supporting artifacts

**Forward Links (Strategic Artifacts):**
- **Downstream Artifacts:** Table tracking what implements this artifact

### 1.7.2 ID Prefix Standards

| Artifact Type | Prefix | Example | Pattern |
|---------------|--------|---------|---------|
| Product Vision | VIS | VIS-001 | VIS-XXX |
| Initiative | INIT | INIT-042 | INIT-XXX |
| Epic | EPIC | EPIC-123 | EPIC-XXX |
| PRD | PRD | PRD-005 | PRD-XXX |
| High-Level Story | HLS | HLS-078 | HLS-XXX |
| Backlog Story | US | US-234 | US-XXX |
| Spike | SPIKE | SPIKE-042 | SPIKE-XXX |
| ADR | ADR | ADR-008 | ADR-XXX |
| Tech Spec | SPEC | SPEC-015 | SPEC-XXX |
| Implementation Task | TASK | TASK-567 | TASK-XXX |

**Research Artifacts:** No document IDs (use descriptive file names)

### 1.7.3 Status Value Standards

**Research Artifacts (Business Research, Implementation Research):**
- `Draft` - In progress, not ready for consumption
- `In Review` - Under review by stakeholders
- `Finalized` - Approved and ready to inform downstream artifacts

**Strategic Artifacts (Vision, Initiative, Epic):**
- `Draft` - Initial creation
- `In Review` - Stakeholder review
- `Approved` - Approved for execution
- `Planned` - (Epic only) Approved and scheduled
- `Active` - (Initiative only) Execution underway
- `In Progress` - Work in progress
- `Completed` - All success criteria met
- `Cancelled` - (Initiative only) Terminated before completion

**Requirements Artifacts (PRD, High-Level Story):**
- `Draft` - Initial creation
- `In Review` - Stakeholder review
- `Approved` - Approved for breakdown
- `Ready` - (Story only) Ready for sprint planning
- `In Progress` - Breakdown or implementation underway
- `Completed` - All requirements implemented

**Implementation Artifacts (Backlog Story, Task):**
- `Backlog` - Identified but not ready for sprint
- `Ready` - Ready for sprint planning
- `To Do` - (Task only) In sprint backlog
- `In Progress` - Implementation underway
- `In Review` - Code review or QA
- `Done` - Accepted by product owner

**Spike Artifacts:**
- `Planned` - Investigation scheduled
- `In Progress` - Investigation underway
- `Completed` - Findings documented

**Architecture Artifacts (ADR, Tech Spec):**
- `Proposed` - Decision/design proposed
- `Accepted` - Approved for implementation
- `Active` - Currently in use
- `Deprecated` - No longer recommended
- `Superseded` - Replaced by newer decision/spec

### 1.7.4 Research Integration Guidelines

**Business Research Integration:**

Business Research informs **business-level artifacts** (strategic planning and user-facing requirements):
- **Product Vision** - Market positioning, user personas, success metrics
- **Initiative** - Strategic justification, market opportunity
- **Epic** - Market gaps, capability recommendations, user needs
- **PRD** (optional) - Market context, competitive positioning (when needed)
- **High-Level Story** (optional) - User persona details (when needed)

**Reference Format:**
```markdown
## Business Research References
**Primary Research:** [Link to Business Research document]

**Applied Insights:**
- **§[X.Y]: [Section Title]:** [How insight applies]
```

**Implementation Research Integration:**

Implementation Research informs **technical artifacts** (implementation planning and execution):
- **PRD** (optional) - Technical feasibility, NFRs (when needed)
- **Backlog Story** - Technical patterns, architecture context
- **Spike** - Investigation baseline, existing patterns
- **ADR** - Architecture patterns, technology comparisons
- **Tech Spec** - Implementation patterns, code examples
- **Implementation Task** - Detailed code examples, anti-patterns to avoid

**Reference Format:**
```markdown
## Implementation Research References
**Primary Research:** [Link to Implementation Research document]

**Technical Patterns Applied:**
- **§[X.Y]: [Pattern Name]:** [How pattern applies]
  - **Code Example:** [Reference if applicable]
```

### 1.7.5 Traceability Matrix

**Complete Upstream/Downstream Relationships:**

| Artifact | Parent | Informed By | Children | Informs |
|----------|--------|-------------|----------|---------|
| Business Research | None | None | None | Vision, Initiative, Epic, PRD, HLS |
| Implementation Research | None | None | None | PRD, US, Spike, ADR, Spec, Task |
| Product Vision | None | Business Research | Initiative, Epic | Initiative, Epic |
| Initiative | Product Vision | Business Research | Epic | Epic |
| Epic | Product Vision, Initiative | Business Research | PRD, HLS | PRD, HLS |
| PRD | Epic | Business Research, Impl Research | HLS, US | HLS, US |
| High-Level Story | Epic, PRD | Business Research | US | US |
| Backlog Story | PRD, HLS | Implementation Research | Spike, ADR, Spec, Task | Technical artifacts |
| Spike | US, Spec | Implementation Research | ADR, Spec | ADR, Spec |
| ADR | US | Spike, Impl Research | Spec, Task | Spec, Task |
| Tech Spec | US, ADR | Spike, Impl Research | Task | Task |
| Task | US, Spec, ADR | Implementation Research | None | None |

### 1.7.6 Validation Best Practices

**Before Marking Artifact as "Approved" or "Ready":**
1. Verify all parent fields link to approved parent artifacts
2. Confirm all research references point to finalized research documents
3. Check that all section references (§X.Y) exist in referenced documents
4. Update parent artifact's downstream tracking table

**When Updating an Existing Artifact:**
1. Review downstream artifacts table to identify affected children
2. Notify owners of downstream artifacts about changes
3. Update version number and status
4. Add change log entry

**Quarterly Traceability Audit:**
1. Validate all artifact links are not broken
2. Check that downstream tracking tables are current
3. Verify research documents are referenced consistently
4. Identify any orphaned artifacts (no parent references)
```

---

### 5.3 Create Traceability Validation Script (Optional - Tooling)

**File:** `scripts/validate_traceability.sh` (future enhancement)

**Purpose:**
- Parse all SDLC artifacts in `/artifacts` directory
- Extract metadata fields (Parent, Informed By, etc.)
- Validate that referenced artifact IDs exist
- Check that status values are standardized
- Report broken links and missing references
- Generate traceability graph visualization

**Example Output:**
```
Traceability Validation Report
Generated: 2025-10-11

✅ PASSED: 45 artifacts validated
❌ FAILED: 3 artifacts with issues

Issues Found:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. PRD-003: Missing Parent Epic field
2. US-042: References non-existent PRD-999
3. EPIC-005: Parent Vision link broken (VIS-001 not found)

Warnings:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. US-023: Parent PRD-002 status is "Draft" (not approved)
2. SPEC-007: Informed By Spike field empty (optional but recommended)

Traceability Graph: ./traceability_graph.svg
```

---

## Implementation Schedule

### Week 1 Timeline

| Day | Phase | Templates Updated | Estimated Hours |
|-----|-------|-------------------|-----------------|
| **Day 1** | Phase 1.1-1.3 | Product Vision, Initiative, Epic | 4-6 hours |
| **Day 2** | Phase 1.4-1.6 | PRD, HLS, Backlog Story | 4-6 hours |
| **Day 3** | Phase 2.1-2.2 | ADR, Tech Spec | 3-4 hours |
| **Day 4** | Phase 2.3 | Implementation Task | 2-3 hours |
| **Day 5** | Phase 3.1-3.2 | Business Research, Implementation Research | 3-4 hours |

**Total Week 1:** ~20-25 hours

### Week 2 Timeline

| Day | Phase | Templates Updated | Estimated Hours |
|-----|-------|-------------------|-----------------|
| **Day 1** | Phase 3.3 | Product Vision (forward links) | 2-3 hours |
| **Day 2** | Phase 3.4 | Epic (forward links) | 2-3 hours |
| **Day 3** | Phase 3.5 | PRD (forward links) | 3-4 hours |
| **Day 4** | Testing | Validate all changes, test with sample artifact | 4-5 hours |
| **Day 5** | Documentation | Update examples in all templates | 3-4 hours |

**Total Week 2:** ~15-20 hours

### Week 3 Timeline

| Day | Phase | Templates Updated | Estimated Hours |
|-----|-------|-------------------|-----------------|
| **Day 1** | Phase 4.1 | Status standardization (all 12 templates) | 4-5 hours |
| **Day 2** | Phase 4.2 | Parent field naming (6 templates) | 3-4 hours |
| **Day 3** | Phase 4.3 | ID prefix standardization (4 templates) | 2-3 hours |
| **Day 4** | Testing | Validate consistency across templates | 3-4 hours |
| **Day 5** | Buffer | Address issues from testing | 3-4 hours |

**Total Week 3:** ~15-20 hours

### Week 4 Timeline

| Day | Phase | Deliverables | Estimated Hours |
|-----|-------|-------------|-----------------|
| **Day 1** | Phase 5.1 | Add validation checklists (all templates) | 4-5 hours |
| **Day 2** | Phase 5.2 | Update SDLC guideline document | 4-5 hours |
| **Day 3** | Phase 5.3 (optional) | Create validation script concept | 3-4 hours |
| **Day 4** | Final Review | Review all templates, test workflow | 4-5 hours |
| **Day 5** | Documentation | Create migration guide for existing artifacts | 3-4 hours |

**Total Week 4:** ~18-23 hours

**Grand Total Effort:** ~70-90 hours (2-2.5 weeks full-time, or 4 weeks at 50% allocation)

---

## Testing & Validation Strategy

### Test Scenario 1: End-to-End Traceability

**Objective:** Verify complete traceability from Business Research to Implementation Task

**Test Case:**
1. Create Business Research document (finalized)
2. Create Product Vision referencing Business Research
3. Create Epic referencing Product Vision and Business Research
4. Create PRD referencing Epic
5. Create Backlog Story referencing PRD and Implementation Research
6. Create Tech Spec referencing Backlog Story and Implementation Research
7. Create Implementation Task referencing Tech Spec and Implementation Research

**Validation:**
- [ ] All "Parent" fields correctly link to parents
- [ ] All "Informed By" fields correctly link to research documents
- [ ] Forward links in Business Research list Vision, Epic, PRD, Story
- [ ] Forward links in Implementation Research list Story, Tech Spec, Task
- [ ] No broken links
- [ ] All section references (§X.Y) are valid

---

### Test Scenario 2: Spike-Driven Decision Flow

**Objective:** Verify traceability through spike investigation workflow

**Test Case:**
1. Create Backlog Story with open question marked [REQUIRES SPIKE]
2. Create Spike referencing parent Backlog Story
3. Complete Spike with recommendation
4. Create ADR based on Spike findings, referencing both Spike and parent Story
5. Create Tech Spec referencing ADR and Spike
6. Update Backlog Story with Spike findings

**Validation:**
- [ ] Spike has "Parent: US-XXX" field populated
- [ ] Spike has "Informs" section listing ADR and Tech Spec
- [ ] ADR has "Informed By Spike: SPIKE-XXX" field
- [ ] Tech Spec has "Informed By Spike: SPIKE-XXX" field
- [ ] Backlog Story Open Questions updated with spike findings
- [ ] All links bidirectional and valid

---

### Test Scenario 3: Initiative-Driven Epic Creation

**Objective:** Verify traceability for initiative-based epic planning

**Test Case:**
1. Create Product Vision referencing Business Research
2. Create Initiative referencing Product Vision and Business Research
3. Create Epic referencing both Initiative and Product Vision
4. Validate forward links updated in Vision and Initiative

**Validation:**
- [ ] Initiative has "Parent Product Vision: VIS-XXX" field
- [ ] Epic has both "Parent Product Vision: VIS-XXX" and "Parent Initiative: INIT-XXX" fields
- [ ] Product Vision "Downstream Artifacts" section lists Initiative and Epic
- [ ] Initiative "Supporting Epics" table includes Epic
- [ ] All Business Research references are valid

---

## Migration Guide for Existing Artifacts

### For Artifacts Created Before Metadata Refinement

**Step 1: Identify Existing Artifacts**
```bash
find ./artifacts -name "*.md" -type f
```

**Step 2: Prioritize Migration**
1. **Active artifacts (In Progress status):** Migrate immediately
2. **Approved artifacts referenced by active work:** Migrate within 1 week
3. **Completed artifacts:** Migrate opportunistically

**Step 3: Add Missing Metadata Fields**

For each artifact:
1. Identify artifact type and locate updated template
2. Compare existing metadata to new template metadata section
3. Add missing fields:
   - Parent artifact links
   - Informed By research links
   - Downstream artifacts table (if strategic artifact)
4. Update status value to standardized value (if changed)
5. Rename field labels for consistency (e.g., "Story ID" → "Parent Story ID")
6. Add traceability validation checklist
7. Bump version number (e.g., v3 → v4) and add change log entry

**Step 4: Update Parent Artifacts**

If artifact has parents:
1. Open parent artifact
2. Add this artifact to parent's "Downstream Artifacts" table
3. Bump parent version and add change log entry

**Step 5: Validate Links**

Run validation checks:
- All parent links point to existing artifacts
- All research links point to existing research documents
- All section references (§X.Y) exist
- All artifact IDs follow new prefix standards

---

## Rollout Communication

### Announcement Template (for Team)

**Subject:** SDLC Artifact Templates - Metadata Enhancements for Traceability

**Summary:**
We're enhancing our SDLC artifact templates to improve traceability and impact analysis. Key changes include:

1. **Explicit Parent Links:** All artifacts now reference their direct parent (e.g., PRD → Epic)
2. **Research Integration:** Business and Implementation Research are explicitly linked
3. **Bidirectional Tracking:** Strategic artifacts track what implements them
4. **Standardized Fields:** Consistent naming and status values across all artifacts

**Timeline:**
- **Week 1-2:** Template updates completed
- **Week 3:** Migration guide published
- **Week 4:** Office hours for questions

**Action Required:**
- **For new work:** Use updated templates (available in `/prompts/templates`)
- **For active work:** Migrate existing artifacts using migration guide
- **For completed work:** No immediate action (migrate opportunistically)

**Questions?** Contact [Name] or attend office hours [Schedule]

---

## Success Criteria

**Phase 1 Success (Week 1):**
- [ ] All 6 critical templates updated with parent links
- [ ] Sample artifacts created demonstrating new metadata
- [ ] No broken links in test artifacts
- [ ] Team review completed

**Phase 2 Success (Week 1):**
- [ ] Research integration fields added to 8 templates
- [ ] Sample artifacts demonstrate research references
- [ ] Section references (§X.Y) validated in examples

**Phase 3 Success (Week 2):**
- [ ] Bidirectional links added to 5 strategic templates
- [ ] Forward tracking tables present and functional
- [ ] Test artifacts demonstrate full traceability chain

**Phase 4 Success (Week 3):**
- [ ] Status values standardized across all templates
- [ ] Parent field naming consistent
- [ ] ID prefixes standardized
- [ ] Consistency validated in test artifacts

**Phase 5 Success (Week 4):**
- [ ] Validation checklists added to all templates
- [ ] SDLC guideline document updated
- [ ] Migration guide published
- [ ] Team training completed

**Overall Success Metrics:**
- Traceability completeness: 90%+ (up from 45%)
- Artifact creation time: <10% increase (due to added fields)
- Link validation: 100% of links valid in new artifacts
- Team adoption: 100% of new artifacts use updated templates within 2 weeks
- Impact analysis: Ability to identify all downstream artifacts when upstream changes

---

**Document Owner:** Context Engineering Team
**Next Review:** After Phase 1 completion (Week 1)
**Feedback:** [Link to feedback form or GitHub issues]

## ROLE
You are a senior software product manager specializing in SDLC optimization and documentation analysis.

## PRE-RESEARCH CLARIFICATION PHASE

**MANDATORY: Complete ALL clarifications before proceeding to research phase. Do NOT make assumptions.**

### Step 1: Validate Context Understanding
Before beginning research, explicitly confirm:

1. **SDLC Template Inventory** - List all template files you will analyze:
   - [ ] Business Research template path: `prompts/templates/[SPECIFY_EXACT_FILENAME]`
   - [ ] Initiative template path: `prompts/templates/[SPECIFY_EXACT_FILENAME]`
   - [ ] Epic template path: `prompts/templates/[SPECIFY_EXACT_FILENAME]`
   - [ ] PRD template path: `prompts/templates/[SPECIFY_EXACT_FILENAME]`
   - [ ] High-Level Story template path: `prompts/templates/[SPECIFY_EXACT_FILENAME]`
   - [ ] Backlog Story template path: `prompts/templates/[SPECIFY_EXACT_FILENAME]`
   - [ ] Any other relevant templates identified in `prompts/templates/`

2. **Problem Scope Validation** - Confirm understanding of reported issues:
   - [ ] "Errors in Happy Paths" - What specific types of errors? (logic gaps, missing steps, incorrect sequence, incomplete scenarios?)
   - [ ] "Errors in error scenarios" - What aspects are problematic? (missing edge cases, incorrect handling, incomplete recovery paths?)
   - [ ] "Errors in input/output definitions" - What's missing or incorrect? (data types, validation rules, schemas, examples, constraints?)
   - [ ] Are there example artifacts demonstrating these issues? If yes, list paths.

3. **Team Context Validation**:
   - [ ] Team size: [SPECIFY NUMBER]
   - [ ] Current roles involved in artifact review: [LIST ROLES]
   - [ ] Average time spent reviewing each artifact type: [SPECIFY IF KNOWN]
   - [ ] Which artifact types consume most review time? [RANK 1-5]

4. **Success Criteria Clarification**:
   - [ ] What is acceptable level of information overlap between artifacts? (0-5%, 5-10%, 10-15%?)
   - [ ] Which mistakes are highest priority to eliminate? (Happy paths? Error scenarios? I/O definitions? All equal?)
   - [ ] Are there any SDLC artifacts that MUST remain unchanged? (regulatory, contractual, etc.)

5. **Research Scope Boundaries**:
   - [ ] Should research cover industry standards (IEEE, PMI, Agile Alliance, etc.)?
   - [ ] Should research include comparisons to specific methodologies (SAFe, Scrum, LeSS, etc.)?
   - [ ] Are there specific companies/teams whose SDLC practices should be studied?
   - [ ] Time period for research sources: [2024-2025 only, or include earlier?]

### Step 2: Present Clarification Summary
Before proceeding to research, present a structured summary:

```
CLARIFICATION SUMMARY
=====================

Templates to Analyze:
- [List with full paths]

Problem Focus Areas (ranked):
1. [Highest priority issue]
2. [Second priority]
3. [Third priority]

Team Context:
- Team size: [N]
- Review bottleneck: [artifact type]

Success Criteria:
- Target overlap reduction: [X%]
- Must-eliminate mistakes: [list]

Research Scope:
- Standards: [yes/no + which]
- Methodologies: [list]
- Time period: [range]

Known Constraints:
- [List any artifacts that cannot change]
```

**→ STOP HERE and wait for user confirmation before proceeding to research phase.**

---

## CONTEXT
Our SDLC Workflow contains a range of documents (Initiative, Epic, PRD, High-level Stories, Backlog Stories). These documents contain comprehensive information on various subjects, spanning from business to implementation. In addition we have business and implementation research documents with extensive information related to competition, market gaps, business-oriented goals, frameworks, database selections, and implementation patterns.

### Issues Identified During PoC

**Problem Category 1: Backlog Story Quality Issues**
- Errors/mistakes in Happy Paths and error scenarios (sometimes missing the point significantly)
- Errors in input/output (request/response) definitions
- Missing edge cases and validation rules

**Problem Category 2: Documentation Structure Issues**
- Critical documentation gap exists before Backlog Stories generation
- Industry comparison: Some teams use Functional Specification and/or Detailed Design Specification
- If we introduce additional documents, we must heavily reduce section overlap

**Problem Category 3: Process Efficiency Issues**
- Business-related sections bloat in current documentation
- Small agile team spending excessive resources verifying all SDLC artifacts
- Reducing unnecessary information would significantly increase efficiency

## GOALS
1. **Identify documentation gaps** in our SDLC workflow (specifically gaps causing Backlog Story mistakes)
2. **Reduce information overlap** across artifacts (quantify current overlap, set reduction target)
3. **Improve team efficiency** by eliminating redundant verification work

## RESEARCH PHASE TASKS

### Task 1: Industry Standards Research
**Objective:** Identify SDLC documents that bridge the gap between PRD/High-Level Stories and Backlog Stories

**Research Questions:**
- What documents do mature software teams use between requirements and implementation?
- Which documents specifically address:
  - Detailed happy path flows (step-by-step logic)?
  - Comprehensive error scenarios (edge cases, failure modes)?
  - Precise input/output contracts (request/response schemas, validation rules)?
- How do industry standards (IEEE 29148, ISO/IEC 12207, Agile methodologies) handle this transition?

**Expected Output:**
- List of candidate document types (Functional Spec, Design Spec, API Spec, etc.)
- For each: purpose, content structure, when used, benefits
- Citations to industry sources [^N]

### Task 2: Template Analysis
**Objective:** Map current coverage and identify gaps

**Analysis Steps:**
1. **Load all templates** (paths confirmed in Clarification Phase)
2. **Extract section inventory** - Create structured list:
   ```
   Template: [name]
   Sections:
   - Section Name | Content Type | Detail Level | Overlaps With
   ```
3. **Identify coverage gaps** for problem areas:
   - Happy Paths: Which template covers detailed step-by-step flows?
   - Error Scenarios: Which template covers comprehensive edge cases?
   - I/O Definitions: Which template defines precise data contracts?
4. **Quantify overlap** - Create overlap matrix:
   ```
   Section Topic | Initiative | Epic | PRD | HLS | Backlog Story | Overlap %
   ```

**Expected Output:**
- Section inventory table (all templates)
- Gap analysis report (missing coverage for problem areas)
- Overlap matrix with percentages

### Task 3: Root Cause Analysis
**Objective:** Determine why Backlog Story mistakes occur

**Analysis Framework:**
- **Gap Hypothesis:** Mistakes occur because [specific information type] is not documented before Backlog Story generation
- **Overlap Hypothesis:** Mistakes occur because information is spread across multiple artifacts, causing inconsistency
- **Process Hypothesis:** Mistakes occur because generators lack explicit inputs for [specific areas]

**Expected Output:**
- Root cause statement with supporting evidence
- Link between documentation gaps and specific mistake types

### Task 4: Optimization Recommendations
**Objective:** Propose lean documentation structure

**Recommendation Framework:**
For each recommendation, provide:
1. **Problem Addressed:** [Which mistake type or efficiency issue]
2. **Proposed Solution:** [Add document X, remove sections Y, consolidate Z]
3. **Impact Analysis:**
   - Gap Coverage: [How it addresses missing information]
   - Overlap Reduction: [Estimated % reduction]
   - Efficiency Gain: [Time saved per artifact cycle]
4. **Implementation Path:** [Concrete steps to implement]
5. **Trade-offs:** [What we lose, if anything]
6. **Supporting Evidence:** [Industry citations [^N]]

**Specific Recommendations Required:**
- Should we add Functional Specification or Detailed Design Specification?
- Which existing sections should be consolidated or removed?
- How should information flow between artifacts be restructured?
- What minimum information is needed at each SDLC phase?

**Expected Output:**
- Prioritized list of recommendations (highest impact first)
- For top 3-5 recommendations: detailed analysis per framework above
- Proposed revised SDLC flow diagram (before/after)

### Task 5: Implementation Roadmap
**Objective:** Provide actionable next steps

**Roadmap Components:**
1. **Phase 1 (Immediate):** Quick wins - changes requiring minimal effort
2. **Phase 2 (Short-term):** Template modifications - revise existing templates
3. **Phase 3 (Medium-term):** New artifacts - introduce new document types
4. **Validation Plan:** How to measure success (reduction in mistakes, review time, etc.)

**Expected Output:**
- Phased implementation plan with timeline estimates
- Success metrics and measurement approach

## OUTPUT REQUIREMENTS

### Document Structure
Save final report at: `docs/lean/report.md`

**Required Sections:**
1. **Executive Summary** (1 page max)
   - Key findings in 3-5 bullet points
   - Top 3 recommendations with expected impact
   - Recommended next steps

2. **Clarification Summary** (from Pre-Research Phase)
   - Reproduce the clarification summary confirmed with user
   - List any assumptions made (with justification)

3. **Current State Analysis**
   - Template section inventory (from Task 2)
   - Overlap matrix with percentages (from Task 2)
   - Gap analysis (from Task 2)

4. **Root Cause Analysis** (from Task 3)
   - Hypothesis validation
   - Evidence linking gaps to mistakes

5. **Industry Research Findings** (from Task 1)
   - Document types analysis
   - Best practices for bridging requirements-to-implementation gap
   - All findings cited [^N]

6. **Recommendations** (from Task 4)
   - Prioritized list (highest impact first)
   - Detailed analysis for top 3-5 recommendations
   - Before/after SDLC flow diagram

7. **Implementation Roadmap** (from Task 5)
   - Phased approach with timelines
   - Success metrics
   - Risk mitigation

8. **References**
   - All citations in format: `[^N]: Full Title, URL, Access Date`
   - Minimum 10 authoritative sources required

9. **Appendices**
   - A: Full template section inventory
   - B: Overlap matrix detailed data
   - C: Areas for Further Research

### Writing Standards
- **Format:** Markdown with proper heading hierarchy
- **Language:** Professional, user-centric, appropriate for product managers and executives
- **Perspective:** Business and process optimization (avoid specific technology prescriptions)
- **Tone:** Objective, evidence-based, actionable
- **Length:** 15-25 pages (excluding appendices)

### Quality Standards
- **Completeness:** All 5 research tasks addressed
- **Evidence:** Every claim supported by citation or data analysis
- **Actionability:** Recommendations include concrete implementation steps
- **Clarity:** Non-technical stakeholders can understand and act on findings

## ANTI-HALLUCINATION GUIDELINES

**CRITICAL: Follow these rules to ensure accuracy and verifiability.**

### Evidence Requirements
- [ ] Base all analysis on actual industry standards (IEEE, ISO, PMI, Agile Alliance, etc.)
- [ ] Use documented SDLC workflows from authoritative sources
- [ ] Reference published research, case studies, and industry reports
- [ ] Every factual claim MUST include citation [^N] with full URL
- [ ] Every statistic MUST include source and date
- [ ] Every "industry practice" claim MUST cite specific examples

### Prohibited Behaviors
- ❌ **DO NOT speculate** - If information unavailable, explicitly state: "Information not available in public sources as of [date]"
- ❌ **DO NOT generalize** - Replace "many teams use..." with "Teams at [Company A], [Company B] use... [^N]"
- ❌ **DO NOT assume** - Replace "best practice" with "practice recommended by [source] for [context] [^N]"
- ❌ **DO NOT invent statistics** - Never use phrases like "approximately", "around", "typically" without citation
- ❌ **DO NOT drift into implementation** - Stay within product/process domain, not technical architecture

### Transparency Requirements
- [ ] When making recommendations, explicitly state assumptions
- [ ] Link every recommendation to supporting analysis or citation
- [ ] Identify gaps in available research
- [ ] Create "Areas for Further Research" section listing information gaps
- [ ] Acknowledge limitations (e.g., "Based on publicly available information from [companies/sources]")
- [ ] Distinguish between:
  - **Facts** (cited),
  - **Analysis** (based on template review),
  - **Recommendations** (based on facts + analysis)

### Citation Format
```markdown
According to IEEE 29148, requirements specifications should include [specific content][^1].

[^1]: IEEE Standard 29148-2018 - Systems and software engineering - Life cycle processes - Requirements engineering, https://standards.ieee.org/standard/29148-2018.html, Accessed 2025-01-15
```

### Self-Validation Checklist (Complete before delivering report)
- [ ] Every "X% of teams" claim has citation
- [ ] Every "industry standard" reference includes source
- [ ] Every recommendation links to evidence or analysis
- [ ] "Areas for Further Research" section exists and lists gaps
- [ ] No unsupported generalizations (search for "typically", "usually", "most", "many" without citations)
- [ ] All URLs tested and accessible
- [ ] Research sources dated 2020 or later (unless historical context)
- [ ] Assumptions explicitly stated in dedicated subsection

## PROCESS SUMMARY

**Phase 0: Clarification (Complete First)**
1. Ask all clarification questions
2. Wait for user responses
3. Present clarification summary
4. Get user confirmation → THEN proceed

**Phase 1: Research (After Confirmation)**
1. Industry standards research → Document findings with citations
2. Template analysis → Extract sections, measure overlap
3. Root cause analysis → Link gaps to mistakes

**Phase 2: Analysis**
1. Synthesize findings
2. Develop recommendations with impact analysis
3. Create implementation roadmap

**Phase 3: Documentation**
1. Write report following structure above
2. Complete self-validation checklist
3. Deliver final report at `docs/lean/report.md`

---

**REMINDER: Complete PRE-RESEARCH CLARIFICATION PHASE before beginning research. All research must be cited. No speculation allowed.**

# sdlc-core.md

## Section Rewrite - Decision Hierarchy for Technical Guidance (THE WHOLE SECTION)

**Solutions:**
- `specialized_claude_standards`, `Specialized CLAUDE.md files`, `Hybrid CLAUDE.md Approach` should be referred to as `patterns`
- `CLAUDE.md` should be referred as `pattern` except if it refers to the root CLAUDE.md, which is not correct within Generators
- Explanation of specific patterns files should be located in the root CLAUDE.md (`new_prompts/CLAUDE.md`) file only
   Example: "- patterns-core.md: Core development philosophy and orchestration"
- All paths resolution should be differed to root CLAUDE.md. No path should be located in this file
Examples:
    `**Location:** `new_prompts/CLAUDE/{language}/patterns-*.md` files`
    `**Location:** `artifacts/research/{product_name}_implementation_research.md``




# Generators

## Sections

Section needs to be rewritten:
```xml
      <artifact classification="conditional" type="specialized_claude_standards">
        Specialized CLAUDE.md files provide (IMPLEMENTATION STANDARDS):
        - patterns-core.md: Core development philosophy and orchestration
        - patterns-tooling.md: Unified CLI (Taskfile), UV, Ruff, MyPy, pytest configuration
        - patterns-testing.md: Testing strategy, fixtures, coverage requirements
        - patterns-typing.md: Type hints, annotations, type safety patterns
        - patterns-validation.md: Pydantic models, input validation, security
        - patterns-architecture.md: Project structure, modularity, design patterns
        - Additional domain-specific files: patterns-security.md, patterns-auth.md, etc.

        Use for Technical Notes section alignment, ensuring story references established implementation standards.

        **Classification**: CONDITIONAL - Load when story includes technical guidance that should align with project implementation standards. Treats CLAUDE.md content as authoritative - story supplements (not duplicates) these standards.

        **Hybrid CLAUDE.md Approach:**
        - Technical Notes section references (not duplicates) specialized CLAUDE.md standards
        - Implementation guidance supplements CLAUDE.md with story-specific context
        - Dependencies section lists relevant CLAUDE.md files when applicable
      </artifact>
```

**Solutions:**
- `specialized_claude_standards`, `Specialized CLAUDE.md files`, `Hybrid CLAUDE.md Approach` should be referred to as `patterns`
- `CLAUDE.md` should be referred as `pattern` except if it refers to the root CLAUDE.md, which is not correct within Generators
- Explanation of specific patterns files should be located in the root CLAUDE.md (`new_prompts/CLAUDE.md`) file only
   Example: "- patterns-core.md: Core development philosophy and orchestration"

---

Section needs to be rewritten:
```xml

    <step priority="3.5">
      <action>Enforce CLAUDE.md Precedence Hierarchy (MANDATORY)</action>
      <purpose>Prevent suggesting alternatives when decisions already made</purpose>
      <guidance>
        **CRITICAL: This step prevents quality errors like US-050 (suggesting "chi or gin" when Gin already decided in patterns-http-frameworks.md:238).**

        **3-TIER HIERARCHY:**
        - **Tier 1 (Authoritative):** CLAUDE.md files = "Decisions Made" (use file:line references, NO alternatives)
        - **Tier 2 (Advisory):** Implementation Research = "Fill Gaps" (use ONLY for topics not in CLAUDE.md)
        - **Tier 3 (Supplementary):** Story-specific decisions = "Product Context" (story-specific only)

        **STEP 1: Load all prompts/CLAUDE/{language}/*.md files**
        - Determine project language from context (Python, Go, etc.)
        - Load all patterns-*.md files from prompts/CLAUDE/{language}/ directory
        - Example files: patterns-core.md, patterns-tooling.md, patterns-testing.md, patterns-http-frameworks.md, etc.

        **STEP 2: Extract decisions from CLAUDE.md files**
        - Look for decision indicators: "Recommended", "Default", "Use", "Standard", "Decision:"
        - Extract decision text and line number for each
        - Example: Line 238 of patterns-http-frameworks.md: "Default: Use Gin for Go REST APIs"
        - Example: Line 45 of patterns-tooling.md: "Use UV for Python package management"
        - Example: Line 67 of patterns-testing.md: "pytest with fixtures, 80% coverage minimum"

        **STEP 3: Create "CLAUDE.md Decisions Register"**
        - Build comprehensive list of all covered topics with file:line references
        - Format: {domain}: {decision} (file:line)
        - Example register:
          ```
          HTTP_Framework: Gin (patterns-http-frameworks.md:238)
          Package_Manager: UV (patterns-tooling.md:45)
          Testing_Framework: pytest with fixtures, 80% coverage (patterns-testing.md:67)
          Linter: Ruff (patterns-tooling.md:52)
          Type_Checker: MyPy strict mode (patterns-typing.md:15)
          Database_ORM: SQLAlchemy (patterns-database.md:30)
          ```

        **STEP 4: Cross-check Implementation Research against CLAUDE.md Decisions Register**
        - For each Implementation Research pattern/recommendation:
          - IF topic found in CLAUDE.md Decisions Register:
            → Mark as "[OVERRIDDEN BY CLAUDE.md]"
            → Do NOT include in Technical Requirements section
            → Use CLAUDE.md decision instead with file:line reference
          - ELSE (topic NOT in register):
            → Mark as "[USE - No CLAUDE.md coverage]"
            → Include in Technical Requirements with [CLAUDE.md GAP] label
        - This prevents conflicts and duplication

        **STEP 5: Generate Technical Requirements Section with Strict Hierarchy**

        Structure output as follows:

        ```markdown
        ## Technical Requirements

        **DECISION HIERARCHY:** CLAUDE.md (Authoritative) > Implementation Research (Advisory) > Story-specific (Supplementary)

        ### CLAUDE.md Decisions Applied

        **Established Standards:**
        - **patterns-http-frameworks.md (Go):** Gin per line 238
        - **patterns-tooling.md:** UV + Ruff per lines 20-45
        - **patterns-testing.md:** pytest with fixtures, 80% coverage per line 67
        - **patterns-typing.md:** MyPy strict mode per line 15
        - [Additional patterns-*.md files as applicable]

        **Example (Compliant):**
        Use Gin HTTP framework per patterns-http-frameworks.md:238

        **Example (Non-Compliant - DON'T DO THIS):**
        ❌ "Use chi, gin, or gorilla/mux" (suggests alternatives when Gin decided)

        ### Implementation Research (Gaps Only)

        **Applied Patterns (ONLY for CLAUDE.md gaps):**
        - **§X.Y: Pattern Name:** [Guidance] - `[CLAUDE.md GAP]`

        ### Story-Specific Implementation Guidance
        [Technical approach specific to this story - supplements CLAUDE.md standards]
        ```

        **VALIDATION CHECKPOINT (before proceeding):**
        - [ ] All CLAUDE.md files for project language loaded
        - [ ] Decisions Register created with file:line references
        - [ ] Implementation Research cross-checked against register
        - [ ] No alternatives suggested for CLAUDE.md-decided topics
        - [ ] All CLAUDE.md references include file:line citations
        - [ ] [CLAUDE.md GAP] label used for Implementation Research patterns not covered by CLAUDE.md

        **FAILURE MODE (What NOT to do):**
        ❌ "Use Gin, chi, or gorilla/mux for HTTP framework" (suggests alternatives when Gin already decided)
        ❌ "Consider UV or pip for package management" (suggests alternatives when UV already decided)
        ❌ "Testing framework: pytest or unittest" (suggests alternatives when pytest already decided)

        **SUCCESS MODE (Correct approach):**
        ✅ "Use Gin HTTP framework per patterns-http-frameworks.md:238"
        ✅ "Use UV package manager per patterns-tooling.md:45"
        ✅ "Follow pytest testing patterns per patterns-testing.md:67 (80% coverage minimum)"
        ✅ "Cache invalidation strategy: Time-based TTL with 5-minute expiration - [CLAUDE.md GAP]" (for topics not in CLAUDE.md)
      </guidance>
      <anti_hallucination>
        - Load ALL patterns-*.md files before generating Technical Requirements
        - Create Decisions Register with file:line references for ALL decisions found
        - NEVER suggest alternatives when decision exists in CLAUDE.md
        - Use [CLAUDE.md GAP] label for Implementation Research patterns not covered by CLAUDE.md
        - If CLAUDE.md file missing or unreadable, WARN user and continue with degraded quality
      </anti_hallucination>
    </step>
```

**Solutions:**
- `CLAUDE.md files`, `Specialized CLAUDE.md files`, `Hybrid CLAUDE.md Approach` should be referred to as `patterns`
- No paths should be present (e.g., prompts/CLAUDE/{language}/*.md files)
- `CLAUDE.md` should be referred as `pattern` except if it refers to the root CLAUDE.md, which is not correct within Generators
- All validation should be moved to appropriate validation section with checklists

Example:
```
        **VALIDATION CHECKPOINT (before proceeding):**
        - [ ] All CLAUDE.md files for project language loaded
        - [ ] Decisions Register created with file:line references
        - [ ] Implementation Research cross-checked against register
        - [ ] No alternatives suggested for CLAUDE.md-decided topics
        - [ ] All CLAUDE.md references include file:line citations
        - [ ] [CLAUDE.md GAP] label used for Implementation Research patterns not covered by CLAUDE.md
```

        **CRITICAL: This step prevents quality errors like US-050 (suggesting "chi or gin" when Gin already decided in patterns-http-frameworks.md:238).**

- No references to artifacts (all generators must remain concrete artifact agnostic) (US-050 references)
```
   <purpose>Prevent suggesting alternatives when decisions already made in CLAUDE.md files (US-050 problem)</purpose>
        **CRITICAL: This step prevents quality errors like US-050 (suggesting "chi or gin" when Gin already decided in patterns-http-frameworks.md:238).**
```

- No references to any external recommendations (Lean Analysis Recommendation 2)
```
   <action>Enforce CLAUDE.md Precedence Hierarchy (MANDATORY - Lean Analysis Recommendation 2)</action>
```

---

Applies to all generators:

**IMPORTANT:** Any mentioning of CLAUDE.md in the generator content MUST be avoided

---

# Templates

## Sections

Section needs to be rewritten:
```markdown
## Technical Requirements

**DECISION HIERARCHY:** CLAUDE.md (Authoritative) > Implementation Research (Advisory) > Story-specific (Supplementary)

**Note:** US generator enforces this hierarchy. CLAUDE.md decisions referenced by file+line, alternatives NOT suggested for decided topics.

### CLAUDE.md Decisions Applied

**Established Standards:**
- **patterns-http-frameworks.md (Go):** [e.g., "Gin per line 238"]
- **patterns-tooling.md:** [e.g., "UV + Ruff per lines 20-45"]
- **patterns-testing.md:** [e.g., "pytest with fixtures, 80% coverage"]
- **patterns-typing.md:** [e.g., "MyPy strict mode"]
- **patterns-architecture.md:** [e.g., "Project structure per lines 15-30"]
- [Additional patterns-*.md files]

**Example (Compliant):**
```
Use Gin HTTP framework per patterns-http-frameworks.md:238
```

**Example (Non-Compliant - DON'T DO THIS):**
```
❌ "Use chi, gin, or gorilla/mux" (suggests alternatives when Gin decided)
```

### Implementation Research (Gaps Only)

**Applied Patterns (ONLY for CLAUDE.md gaps):**
- **§[X.Y]: [Pattern]:** [Guidance] - `[CLAUDE.md GAP]`

### Story-Specific Implementation Guidance

[Technical approach specific to this story - supplements CLAUDE.md standards]

### CLAUDE.md Override (If Needed)

```
[CLAUDE.md OVERRIDE] {Alternative}
- Original: patterns-{file}.md:{line}
- Rationale: {Justification}
- Approval: [APPROVED BY: {name}]
```

### Technical Tasks
- [Frontend task - per patterns-architecture.md structure]
- [Backend task - using CLAUDE.md patterns]
- [Database change - per patterns-database.md]
- [Testing task - per patterns-testing.md strategy]
```

**Solutions:**
- `CLAUDE.md files`, `Specialized CLAUDE.md files`, `Hybrid CLAUDE.md Approach` should be referred to as `patterns`
- No paths should be present (e.g., prompts/CLAUDE/{language}/*.md files)
- `CLAUDE.md` should be referred as `pattern` except if it refers to the root CLAUDE.md, which is not correct within Generators
- All validation should be moved to appropriate validation section with checklists

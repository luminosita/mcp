# Specialized Context: Product Vision

**Document Version**: 1.0
**SDLC Phase**: Vision
**Parent Document**: `/CLAUDE.md`

---

## Purpose

This specialized context provides orchestration guidance for the **Product Vision** phase of the SDLC. It supplements the root `/CLAUDE.md` with phase-specific file references, context loading requirements, and iteration patterns specific to this phase.

**IMPORTANT**: This file provides ORCHESTRATION CONTEXT ONLY. Detailed execution instructions, validation checklists, and examples are in the generator prompt (`product_vision_generator_v2.xml`). DO NOT duplicate generator content here.

---

## Domain Expertise for This Phase

**Product Strategy and Market Analysis:**
- Market research methodologies and competitive analysis
- Problem-solution fit validation with quantified data
- User persona development from research
- Strategic goal setting with measurable outcomes (SMART)

---

## File Locations

### Generator Prompt
**Path**: `/prompts/product_vision_generator_v2.xml`
**Contains**: System role, anti-hallucination guidelines, step-by-step instructions, validation checklist, quality guidance, examples

### Template
**Path**: `/prompts/templates/product-vision-template.xml`
**Contains**: Document structure (11 sections), instructions for filling, CDATA with markdown template

### Input Artifact
**Path**: `/docs/product-idea.md`
**Contains**: Initial product concept, problem overview, target users (high-level), key capabilities (draft)

### Output Artifacts
**Terminal Artifact**: `/artifacts/product_vision_v{N}.md` (v1, v2, v3)
**Next Generator**: `/prompts/epic_generator.xml`

---

## Context Loading Requirements

### For Generator Execution (via /execute-generator)

**Mandatory Files to Load**:
- `/CLAUDE.md` (root orchestration)
- `/prompts/CLAUDE-product-vision.md` (this file)
- `/prompts/product_vision_generator_v2.xml` (generator prompt)
- `/prompts/templates/product-vision-template.xml` (output structure)
- `/docs/product-idea.md` (input artifact)

**DO NOT Load** (use tools instead):
- Research documents (use WebSearch for competitive analysis)
- Historical artifacts (not needed for vision phase)
- Full strategy documents (only load if generator references specific sections)

**Context Size Target**: <50% of Claude's context window (< 100k tokens)

---

## Validation Reference

**DO NOT duplicate validation checklist here.**

See generator prompt `/prompts/product_vision_generator_v2.xml` section `<validation_checklist>` for complete criteria.

Summary: Vision v{N} must have 11 complete sections, quantified pain points (3+), SMART metrics, detailed personas (2+), competitive analysis (2+ solutions), and valid XML epic generator.

---

## Common Iteration Patterns

### v1 → v2 (Typical Issues from Experience)

**Observed Patterns**:
- Problem statement lacks quantified data → Add WebSearch results with citations
- Success metrics missing baseline or timeline → Convert to table format with all SMART dimensions
- Personas too generic → Add demographics, behaviors, goals, pain points, technical proficiency
- Competitive analysis skipped → Research 2-3 competitors via WebSearch
- Vision statement too long or feature-focused → Rewrite as single aspirational sentence

**Common Critique Categories**:
- Completeness: Missing sections or placeholder text
- Clarity: Technical jargon without explanation
- Actionability: Vague metrics or capabilities
- Traceability: No references to product-idea.md

### v2 → v3 (Final Refinement Focus)

**Polish Areas**:
- Verify all sections substantive (no placeholders)
- Check traceability: Every claim links to product-idea.md or research source
- Validate epic generator: XML syntax, references correct templates
- Confirm readability for non-technical stakeholders

**Strategy Document Update**:
At v3 completion, HUMAN must manually update `/docs/context_engineering_strategy_v1.md` Section 8.2 with lessons learned from this iteration cycle.

---

## Phase Transition Notes

### Moving to Epic Phase

**Prerequisites**:
- Product Vision v3 approved by human
- Epic generator (`/prompts/epic_generator.xml`) validated as syntactically correct XML
- Strategy document Section 8.2 updated with Product Vision patterns

**Next Phase Context**:
- New session (C2) required for Epic generation
- Epic generator will load product_vision_v3.md as input
- Human approval checkpoint at Epic v3 before proceeding to PRD

---

## Known Pitfalls (Observed from Iterations)

### Pitfall 1: Competitive Research Skipped
**Problem**: Generator produces assumptions about competitors without validation
**Solution**: Always use WebSearch tool to research 2-3 actual competitors; cite sources

### Pitfall 2: Success Metrics Not SMART
**Problem**: Metrics like "Increase productivity" without baseline, target, timeline, measurement method
**Solution**: Use table format with all 5 SMART dimensions (Specific, Measurable, Achievable, Relevant, Time-bound)

### Pitfall 3: Vision Statement Too Long
**Problem**: Multiple sentences describing features rather than aspirational outcome
**Solution**: Rewrite as single sentence focused on user benefit and outcome (not features)

---

## Related Commands

- `/execute-generator TASK-004` - Execute Product Vision Generator v1
- `/refine-generator product_vision_generator_v2` - Refine based on critique (produces v2 or v3)

---

## Execution Workflow Summary

1. **Execute v1**: `/execute-generator TASK-004` in new session
2. **Human creates**: `/feedback/product_vision_v1_critique.md` with structured feedback
3. **Refine to v2**: `/refine-generator product_vision_generator_v2` (loads v1 + critique)
4. **Human creates**: `/feedback/product_vision_v2_critique.md` with remaining issues
5. **Refine to v3**: `/refine-generator product_vision_generator_v2` (loads v2 + critique)
6. **Human approves**: Vision v3 final, updates strategy doc Section 8.2
7. **Proceed**: Move to Epic phase (TASK-009) in new session

---

**Template Version**: 1.0
**Last Updated**: 2025-10-10
**Maintained By**: Context Engineering Framework

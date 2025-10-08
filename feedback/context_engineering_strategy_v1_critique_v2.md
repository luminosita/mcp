## Critiques

- C1: extract specialized CLAUDE.md template into a file from strategy document (Section 4.2 Specialized CLAUDE.md). Reference that file in CLAUDE.md instead of "Generates from template" (Section: Specialized CLAUDE.md Files)

- C2: `product-vision-generator.xml`, evaluate if constraints `[CUSTOMIZE PER PRODUCT]` make any sense/give any value

- C3: main `CLAUDE.md` Step 7, evalute if "- Applies Self-Refine pattern" is clear instruction for LLM or we need additional clarification what "Self-Refine pattern" means (maybe with examples)

- C4: main `CLAUDE.md`, section "Key Research References", confirm that references listed are only for documentation purpose and will NOT be loaded into context for each session

- C5: Strategy document is out-of-sync with TODO.md and requires cleanup:
    - section numbers duplication
    - "Backlog Story Generation" needs to be part of Phase 1
    - uses "/kickoff" prefix


- C6: Additional task: evaluate covered items from the main research document

## Questions

- Q1: do we specify anti-hallucination guardrails (as specified in Section 3: Anti-Hallucination and Factual Grounding Strategies of the main research document) anywhere in generated prompts? Specifially, do we specify instructions for confirming all the assumptions before proceeding?

**CRITICAL** Analyze my critiques, and perform clarification loop by asking questions until all statements are clarified. Give clear answer to evaluate requests. Only proceed with updates upon confirmation.
 
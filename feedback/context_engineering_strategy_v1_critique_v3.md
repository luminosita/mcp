## Critiques

- C1: refine-generator should have a new step (3.1) to instruct AI Agent to clarify all critiques by asking questions to human and only when 100% clear on instructions to proceed with Step 4 (Generate Refinement Plan)
- C2: execute-generator should be updated to use {task_type} metadata instead of {task_name}, since we already updated TODO.md with that additional field
- C3: evaluate if product-vision-generator and generator-schema-template contain instructions for human to confirm all ASSUMPTIONS before proceeding with generation of artifacts and next_generator
- C4: Create plan for implementing recommendations from `docs/research/advanced_prompt_engineering/research_coverage_evaluation.md`

**CRITICAL** Analyze my critiques, and perform clarification loop by asking questions until all statements are clarified. Give clear answer to evaluate requests. Only proceed with updates upon confirmation.
 
## CONTEXT
We created ideal Research prompt and Research Artifact Template covering all critical areas of the information required for sophisticated market/business analysis and crafting of SDLC artifacts guiding well-planned product implementation.
There are two planning phases in SDLC workflow: business/user orientied (values, goals, impact, techincal agnostic), and implementation oriented (technology aware, tasks, backlog)
Primary idea of Research Artifact is to be the primary source of truth for creation of SDLC artifacts. Some of the SDLC artifacts belong to a first (business) planning phase, and some into the second, implementation oriented, with some overlaps. Loading of the huge research artifact containing business analysis, market gaps/niches, further research, technology recommendation and analysis for every SDLC artifact creation can overburden AI context. Solution would be to break down Research Artifact in parts and increase efficiency for SDLC artifact creation.

## GOAL
- Identify overlaps between two planning phases
- Synthesize comprehensive plan for splitting research artifacts, research prompt and research artifact template
- Keep necessary information in each part for creation of corresponding SDCL artifacts

## INSTRUCTIONS
- Do a deep analysis of research prompt and artifact template
- Do a deep analysis of the example research artifact (Backlog Solution) corresponding to the template
- Clarify all assumptions with human by asking questions
- Proceed with the split only after the plan confirmation

## OUTPUT
- Save documents in `docs/research/research_generator`
- No overwrites of existing files

## INPUT
- `prompts/templates/research_artifact_template.md`
- `prompts/research_prompt.xml`
- `docs/research/backlog/Backlog_Solution_Implementation_Guidelines_v2.md`


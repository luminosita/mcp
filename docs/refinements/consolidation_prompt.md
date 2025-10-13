# Refinement plan for generators and artifact templates
## Consolidation of output validation checks in generators
### Current situation
output file and format validation check instructions are in three different locations:
- Instruction step `Internal validation using traceability checklist`
- Output format -> Validation checklist
- Validation -> Self-check

### Proposed Fix
- Evaluate if all validation checks can be consolidated in a fewer locations
- Evaluate if there are overlaps with validation checks
- Consolidate validation checks
**Rationale**: Maintenance burden to high and error-prone with scattered validation instructions

## File paths
### Current situation
File paths exists in several locations:
- CLAUDE.md file, as the main processs orchestrator
- generator sections:
    - system
    - input
    - output
    - validations checks
    - tracebility
- artifact templates
    - metadata (informed by, parent, ...)
    - links and URL
- generate command
- refine command

### Proposed fix
- consolidate all required input and output paths and file naming conventions in CLAUDE.md
- Links/URLs should be specified in the format `{SDLC_DOCUMENTS_URL}/{artifact_type}/{artifact_id}. Example: `{SDLC_DOCUMENTS_URL}/epic/003`, for links referencing EPIC-003 artifact. "{SDLC_DOCUMENTS_URL}" should be kept as a placeholder
**Rationale**: It gives us much flexibility in changing folder structure and moving files from filesystem to MCP http based system

## Synchronization of required/optional input artifacts
### Current situation
There are several sections defining if an artifact is MANDATORY or OPTIONAL as an input for a generator:
- generator input artifacts (required attribute)
- generator input artifacts (description sometimes describe an artifact as OPTIONAL)
- CLAUDE.md ("SDLC Generators Input Dependency Tree" section)

### Proposed Fix
- Evaluate what is the single best location for defining input artifact as required/optional
- Consolidate that definition into one location

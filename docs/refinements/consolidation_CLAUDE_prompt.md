# Consolidation for CLAUDE.md
## Consolidation of artifact, template and generator paths
### Current situation
Paths for artifacts, templates and generators are defined in:
- Artifact Path Patterns section
- Folder Structure
- SDLC Generators Input Dependency Tree

### Proposed Fix
- Consolidate all paths into a single location
**Rationale**: Maintenance burden to high and error-prone with scattered file path instructions

## SDLC Generators Input Dependency Tree section
### Current situation
Artifact generators inputs are defined in several locations:
- In generators, section `<input_artifacts>`, with comprehensive path, naming and classification defined
- In SDLC Generators Input Dependency Tree

### Evaluation
- Q1: do we need SDLC Generators Input Dependency Tree with comprehensive "Input Classification System", "Artifact Path Patterns" and "File Naming Conventions" defined?

## Folder Structure section 
### Current situation
Folder structure define locations of all files in the project. It also contains File Naming convention specified separately in "File Naming Conventions" section.

### Evaluation
What information from Folder Structure section adds value and what are redundant information?


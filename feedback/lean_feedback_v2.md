# Additional Critical Issue

## CONTEXT
There are handful of instructions that hybrid `CLAUDE.md` documents should be treated as architecute guidelines and decisions. PRD-006, in implementation/technical sections only reflected upon implementation research artifact without consulting hybrid `CLAUDE.md` structure for the guideline. Concrete example is with `chi` http framework suggestion for Go microservices, where we already clearly identified Gin as a http framework of choice in CLAUDE.md files for Go. There seems to be a gap in instructions on how/when to use hybrid CLAUDE.md files and that they should take a precedence over implementation research recommendations. Implementation Research recommendations should suggest an alternative within PRD or be primary source if CLAUDE.md files do not cover a particular subject, in which case PRD should contain clear flag that our CLAUDE.md files should be extended to cover additional patterns. Do an analysis on the subject of hybrid files usage and extend the report to include recommendations on that subject as well.

## GOAL
- Identify instruction gaps related to the treatment of hybrid `CLAUDE.md` files
- Recommend the solution for those gaps

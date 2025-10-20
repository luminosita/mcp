# Answers

## Step 2

Q1: "Errors in Happy Paths" - What specific types of errors? (logic gaps, missing steps, incorrect sequence, incomplete scenarios?)
A1: Incorrect sequence most of the time. The rest of the issues are minor

Q2: "Errors in error scenarios" - What aspects are problematic? (missing edge cases, incorrect handling, incomplete recovery paths?)
A2: These just follow issues from A1. Once we resolve Happy Paths, and alternative paths, most of the issues with error scenarios will be gone

Q3: "Errors in input/output definitions" - What's missing or incorrect? (data types, validation rules, schemas, examples, constraints?)
A3: Input/output schemas. Seems like there is a huge amount of assumptions and hallucinations in Happy Paths clarity causing all sorts of hallucinations with input/output (request/response) schema definitions

Q4: Are there example artifacts demonstrating these issues? If yes, please provide paths (e.g., specific US-XXX files with known quality issues)
A4: US-040 -> US-044, US-050, US-051 (latest versions)

---

## Step 3

Q1: Team size:
A1: 10-15

Q2: Current roles involved in artifact review:
A2: Product Manager, Tech Lead, Engineers, QA

Q3: Average time spent reviewing each artifact type:
A3: 1 hour for PRD, 30 min per HLS, 20 min per US + additional hours for refinement, which should be avoided

Q4: Which artifact types consume most review time?
A4: PRD - 5, Epic - 2, HLS - 3, Backlog Story - 4, Tech Spec - 1

**Rationale for A4:**
PRD and HLS has a lot of unnecessary business related sections. EPIC can also be more lean on business side. Initiative seems well balanced

---

## Step 4

Q1: What is acceptable level of information overlap between artifacts?
A1: 5-10%, or which ever seems reasonable to avoid loosing the necessary information for downstream artifact generation

Q2: Which mistakes are highest priority to eliminate?
A2: Happy paths and I/O definitions

Q3: Are there any SDLC artifacts that MUST remain unchanged?
A3: None

**Rationale:**
We not looking just to eliminate sections on random or on some corse criteria (business vs technical). Each downstream artifact heavily depend on the information from the upstream artifacts it references.

---

## Step 5

Q1: Should research cover industry standards? (IEEE 29148, ISO/IEC 12207, PMI, Agile Alliance, etc.)
A1: Yes

Q2: Should research include comparisons to specific methodologies? (SAFe, Scrum, LeSS, Spotify Model, Shape Up, etc.)
A2: Yes

Q3: Are there specific companies/teams whose SDLC practices should be studied? (e.g., Google, Microsoft, Atlassian, GitLab, etc.)
A3: None to suggest

Q4: Time period for research sources:
A4: We should not limit only to 2024-2025. SDLC is not fast changing subject in the industry. The SDLC standards exist already for some time

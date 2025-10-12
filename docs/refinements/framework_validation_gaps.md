# Context Engineering Framework - Validation Gaps

## Document Metadata
- **Version:** 1.0
- **Date:** 2025-10-11
- **Status:** Active
- **Purpose:** Document known validation gaps and recommendations for production deployment

---

## Overview

This document catalogs validation gaps identified during Phase 1 (PoC) execution that should be addressed before production deployment of the Context Engineering Framework.

---

## Gap 1: Input Artifact Status Validation

### Description

The framework currently lacks automated validation to ensure input artifacts have "Approved" status before being used as inputs to downstream generators.

### Current State

**What Exists:**
- File existence validation ✅
- File size validation (context window limits) ✅
- Task completion status checking ✅

**What's Missing:**
- ❌ Input artifact metadata status validation
- ❌ Version verification (v1 vs v3)
- ❌ Approval timestamp tracking

### Impact

**PoC/Development:**
- **Risk Level:** Low (acceptable with documentation)
- **Impact:** May generate downstream artifacts from Draft inputs, requiring regeneration if upstream artifact changes during refinement

**Production:**
- **Risk Level:** High (unacceptable)
- **Impact:** Could cascade unapproved changes downstream, violating approval gates and quality control processes

### Examples of Issue

**TASK-008 (Initiative Generator):**
- **Required Input:** Product Vision v3 (Approved)
- **Actual Input Used:** Product Vision v1 (Draft)
- **Risk:** If Vision v2/v3 significantly changes capabilities or success metrics, Initiative must be regenerated

**TASK-009 (Epic Generator):**
- **Required Input:** Product Vision v3 (Approved)
- **Actual Input Used:** Product Vision v1 (Draft)
- **Risk:** 5 epics may need regeneration if Vision changes

### Recommended Solution

**Validation Check Location:** `.claude/commands/generate.md` Step 2: Load Context & Validate Inputs

**Validation Logic:**
```
1. Parse input artifact metadata section
2. Extract Status field value
3. If Status ≠ "Approved":
   - Production mode: Block execution with error
   - Development mode: Warn and prompt for confirmation
4. Exception: Research phase artifacts (always approved sources)
```

#### Python Implementation Examples

**Strict Mode (Production):**
```python
import re
from pathlib import Path

class ArtifactValidationError(Exception):
    """Raised when artifact validation fails."""
    pass

def validate_artifact_status_strict(artifact_path: str, required_status: str = "Approved") -> bool:
    """
    Validate artifact has required status (strict mode - blocks execution).

    Args:
        artifact_path: Path to artifact file
        required_status: Required status value (default: "Approved")

    Returns:
        True if validation passes

    Raises:
        ArtifactValidationError: If status is invalid or missing
    """
    # Exception: Research artifacts are always approved
    if is_research_artifact(artifact_path):
        return True

    # Read artifact file
    try:
        with open(artifact_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        raise ArtifactValidationError(f"Artifact not found: {artifact_path}")

    # Parse metadata section for Status field
    # Pattern: - **Status:** Draft|Review|Approved|Planned|In Progress|Completed
    status_pattern = r'-\s*\*\*Status:\*\*\s+(\w+(?:\s+\w+)*)'
    status_match = re.search(status_pattern, content)

    if not status_match:
        raise ArtifactValidationError(
            f"ERROR: No status found in artifact metadata\n"
            f"File: {artifact_path}\n\n"
            f"Action Required:\n"
            f"1. Verify artifact has metadata section with Status field\n"
            f"2. Format: - **Status:** Draft|Review|Approved|Planned|In Progress|Completed"
        )

    status = status_match.group(1).strip()

    if status != required_status:
        raise ArtifactValidationError(
            f"ERROR: Input artifact has invalid status for production use\n"
            f"Required: Status = '{required_status}'\n"
            f"Found: Status = '{status}' in {artifact_path}\n\n"
            f"This artifact requires critique and refinement before use as input.\n\n"
            f"Action Required:\n"
            f"1. Complete critique cycle (e.g., TASK-005: Critique Product Vision v1)\n"
            f"2. Refine artifact based on feedback (e.g., TASK-006: Refine to v2)\n"
            f"3. Obtain approval after final refinement (v3)\n"
            f"4. Update artifact status to '{required_status}'\n"
            f"5. Retry generator execution\n\n"
            f"Note: For PoC/development, you may proceed with '{status}' status at risk\n"
            f"of rework if upstream artifact changes significantly during refinement."
        )

    return True

def is_research_artifact(artifact_path: str) -> bool:
    """Check if artifact is a research document (always approved)."""
    research_indicators = [
        'business_research.md',
        'implementation_research.md',
        '/research/',
        '_research_'
    ]
    path_str = str(artifact_path).lower()
    return any(indicator in path_str for indicator in research_indicators)


# Usage example
try:
    validate_artifact_status_strict('/artifacts/product_visions/VIS-001_AI_Agent_MCP_Server_v1.md')
    print("✅ Artifact validation passed")
except ArtifactValidationError as e:
    print(str(e))
    exit(1)
```

**Warning Mode (Development/PoC):**
```python
import re
from pathlib import Path
from typing import Optional

def validate_artifact_status_warning(
    artifact_path: str,
    required_status: str = "Approved",
    allow_override: bool = True
) -> bool:
    """
    Validate artifact status with warning mode (allows override).

    Args:
        artifact_path: Path to artifact file
        required_status: Required status value (default: "Approved")
        allow_override: If True, prompt user to continue; if False, block

    Returns:
        True if validation passes or user confirms override
        False if validation fails and user declines override

    Raises:
        ArtifactValidationError: If critical validation issues (missing file/status)
    """
    # Exception: Research artifacts are always approved
    if is_research_artifact(artifact_path):
        return True

    # Read artifact file
    try:
        with open(artifact_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        raise ArtifactValidationError(f"Artifact not found: {artifact_path}")

    # Parse metadata section for Status field
    status_pattern = r'-\s*\*\*Status:\*\*\s+(\w+(?:\s+\w+)*)'
    status_match = re.search(status_pattern, content)

    if not status_match:
        raise ArtifactValidationError(
            f"ERROR: No status found in artifact metadata\n"
            f"File: {artifact_path}"
        )

    status = status_match.group(1).strip()

    # If status matches requirement, validation passes
    if status == required_status:
        return True

    # Status doesn't match - issue warning
    warning_message = (
        f"\n{'='*70}\n"
        f"⚠️  WARNING: Input Artifact Status Mismatch\n"
        f"{'='*70}\n"
        f"Required Status: '{required_status}'\n"
        f"Found Status:    '{status}'\n"
        f"File:            {artifact_path}\n\n"
        f"RISK: Artifact may change during refinement, requiring regeneration\n"
        f"      of all downstream artifacts.\n\n"
        f"Production Requirement:\n"
        f"  - Complete critique and refinement cycle to v3\n"
        f"  - Obtain human approval\n"
        f"  - Update artifact status to '{required_status}'\n"
        f"  - Then execute generator\n\n"
        f"PoC/Development Exception:\n"
        f"  - You may proceed with '{status}' status for demonstration\n"
        f"  - Document this deviation in task completion notes\n"
        f"  - Monitor upstream artifact changes and regenerate if needed\n"
        f"{'='*70}\n"
    )

    print(warning_message)

    if not allow_override:
        print("❌ Override not allowed in current mode. Execution blocked.")
        return False

    # Prompt user for confirmation
    while True:
        response = input("Continue with non-approved artifact? (yes/no): ").strip().lower()
        if response in ['yes', 'y']:
            print("✅ Proceeding with user confirmation...")
            print("⚠️  Remember to regenerate if upstream artifact changes!\n")
            return True
        elif response in ['no', 'n']:
            print("❌ Execution cancelled by user.")
            return False
        else:
            print("Please enter 'yes' or 'no'")


# Usage example
try:
    validation_passed = validate_artifact_status_warning(
        '/artifacts/product_visions/VIS-001_AI_Agent_MCP_Server_v1.md',
        allow_override=True  # Set to False for stricter validation
    )

    if not validation_passed:
        print("Validation failed. Exiting...")
        exit(1)

    print("Proceeding with generator execution...\n")
    # Continue with generator execution

except ArtifactValidationError as e:
    print(str(e))
    exit(1)
```

**Integration with Generate Command:**
```python
def execute_generator(task_id: str, validation_mode: str = "warning"):
    """
    Execute generator with artifact validation.

    Args:
        task_id: Task ID from TODO.md (e.g., "TASK-008")
        validation_mode: "strict" | "warning" | "disabled"
    """
    # Step 1: Parse task from TODO.md
    task = parse_task_from_todo(task_id)

    # Step 2: Load context and validate inputs
    print(f"Loading context for {task_id}...")

    # Validate input artifacts
    for artifact_path in task.input_artifacts:
        print(f"Validating: {artifact_path}")

        try:
            if validation_mode == "strict":
                validate_artifact_status_strict(artifact_path)
                print(f"  ✅ Status: Approved")

            elif validation_mode == "warning":
                validation_passed = validate_artifact_status_warning(artifact_path)
                if not validation_passed:
                    print(f"  ❌ Validation failed for {artifact_path}")
                    return False

            elif validation_mode == "disabled":
                print(f"  ⚠️  Validation disabled - proceeding without checks")

            else:
                raise ValueError(f"Invalid validation_mode: {validation_mode}")

        except ArtifactValidationError as e:
            print(f"  ❌ Validation error:\n{e}")
            return False

    # Step 3: Execute generator
    print(f"\nExecuting generator for {task_id}...")
    output = run_generator(task)

    # Step 4: Validate output artifact has Status: Draft
    validate_output_status(output.artifact_path, expected_status="Draft")

    print(f"\n✅ {task_id} completed successfully")
    print(f"   Output: {output.artifact_path}")
    return True


# Example usage
if __name__ == "__main__":
    import sys

    # Production mode: strict validation
    # execute_generator("TASK-008", validation_mode="strict")

    # Development mode: warning with override
    execute_generator("TASK-008", validation_mode="warning")

    # PoC mode: validation disabled
    # execute_generator("TASK-008", validation_mode="disabled")
```

**Helper Functions:**
```python
def validate_output_status(artifact_path: str, expected_status: str = "Draft") -> bool:
    """
    Validate newly generated artifact has correct initial status.

    Args:
        artifact_path: Path to generated artifact
        expected_status: Expected status (default: "Draft")

    Returns:
        True if validation passes

    Raises:
        ArtifactValidationError: If status is incorrect
    """
    with open(artifact_path, 'r', encoding='utf-8') as f:
        content = f.read()

    status_pattern = r'-\s*\*\*Status:\*\*\s+(\w+(?:\s+\w+)*)'
    status_match = re.search(status_pattern, content)

    if not status_match:
        raise ArtifactValidationError(
            f"Generated artifact missing Status field: {artifact_path}"
        )

    status = status_match.group(1).strip()

    if status != expected_status:
        raise ArtifactValidationError(
            f"Generated artifact has incorrect status\n"
            f"Expected: '{expected_status}'\n"
            f"Found: '{status}'\n"
            f"File: {artifact_path}\n\n"
            f"All generated artifacts must start with Status: {expected_status}"
        )

    return True


def parse_artifact_metadata(artifact_path: str) -> dict:
    """
    Parse artifact metadata section into dictionary.

    Returns:
        Dictionary with metadata fields (Epic ID, Status, Priority, etc.)
    """
    with open(artifact_path, 'r', encoding='utf-8') as f:
        content = f.read()

    metadata = {}

    # Extract metadata section (between ## Metadata and next ##)
    metadata_pattern = r'## Metadata\s*(.*?)(?=\n##|\Z)'
    metadata_match = re.search(metadata_pattern, content, re.DOTALL)

    if metadata_match:
        metadata_text = metadata_match.group(1)

        # Parse each field: - **Field:** Value
        field_pattern = r'-\s*\*\*([^:]+):\*\*\s*(.+?)(?=\n-|\n\n|\Z)'
        for match in re.finditer(field_pattern, metadata_text, re.DOTALL):
            field_name = match.group(1).strip()
            field_value = match.group(2).strip()
            metadata[field_name] = field_value

    return metadata


# Example usage
metadata = parse_artifact_metadata('/artifacts/epics/EPIC-001_project_management_integration_v1.md')
print(f"Epic ID: {metadata.get('Epic ID')}")
print(f"Status: {metadata.get('Status')}")
print(f"Priority: {metadata.get('Priority')}")
```

### Implementation Priority

**Phase 1 (PoC):** Documented gap, no implementation required ✅

**Phase 2 (Production):** Critical - Must implement before production deployment

**Recommended Approach:**
- Implement validation logic in generate command
- Add configuration flag: `validation.mode = strict | warning | disabled`
- Development: Warning mode (allow override with confirmation)
- Production: Strict mode (block execution)

---

## Gap 2: New Session Enforcement

### Description

Framework specifies that most tasks require fresh Claude Code sessions, but there's no automated enforcement mechanism to ensure sessions are started/ended per task requirements.

### Current State

**What Exists:**
- Documentation in CLAUDE.md specifying new session requirements ✅
- TODO.md task metadata with "Context: New session CX required" ✅

**What's Missing:**
- ❌ Automated session state tracking
- ❌ Validation that generator runs in clean context
- ❌ Session boundary enforcement

### Impact

**PoC/Development:**
- **Risk Level:** Low (single session acceptable for demonstration)
- **Impact:** Context window usage may be higher; potential for context bleeding between tasks

**Production:**
- **Risk Level:** Medium (process issue, not data integrity)
- **Impact:**
  - Context overflow risk with large artifacts
  - Information bleeding between generator executions
  - Non-reproducible results if context state varies

### Examples of Issue

**TASK-008 and TASK-009:**
- **Required:** New sessions C2, C3
- **Actual:** Executed in continuous session from TASK-004
- **Risk:** Context accumulated from Product Vision generation may influence Initiative/Epic generation

### Recommended Solution

**Manual Process (Acceptable for PoC):**
- Human operator follows TODO.md context requirements
- Start/end sessions based on task metadata

**Automated Enforcement (Production):**
- Session state tracking in framework
- Validation that context is clean before generator execution
- Automated session management in orchestration layer

### Implementation Priority

**Phase 1 (PoC):** Documented gap, manual process acceptable ✅

**Phase 2 (Production):** Medium priority - Implement if framework used at scale with multiple operators

---

## Gap 3: Artifact Version Tracking

### Description

Framework lacks explicit version tracking in artifact metadata and dependency resolution to ensure correct version (v3) is loaded as input.

### Current State

**What Exists:**
- Filename versioning convention: `{artifact}_v{1-3}.md` ✅
- Dependency tree specifies version requirements (e.g., v3 for approved) ✅

**What's Missing:**
- ❌ Version field in artifact metadata
- ❌ Automated version resolution (load v3 automatically)
- ❌ Version compatibility checks

### Impact

**PoC/Development:**
- **Risk Level:** Low (manual file path management acceptable)
- **Impact:** Human operator must remember to use correct version file

**Production:**
- **Risk Level:** Medium (operational risk)
- **Impact:** Easy to accidentally load wrong version (v1 instead of v3)

### Recommended Solution

**Short-term:**
- Update TODO.md to explicitly specify file paths with versions
- Document version requirements in task descriptions

**Long-term:**
- Add Version field to artifact metadata
- Implement version resolution logic: "load latest approved version"
- Add version compatibility matrix in dependency tree

### Implementation Priority

**Phase 1 (PoC):** Documented gap, manual process acceptable ✅

**Phase 2 (Production):** Low-Medium priority - Quality of life improvement

---

## Gap 4: Generated Artifact Status Enforcement

### Description

Framework must ensure all newly generated artifacts have Status set to "Draft" to prevent premature progression through the approval lifecycle.

### Current State

**What Exists:**
- Documentation requirement in generate.md Step 3 ✅
- Status lifecycle documented: Draft → Review → Approved → Planned → In Progress → Completed ✅
- Validation check in Report Results section ✅

**What's Missing:**
- ❌ Automated enforcement (validation that Status = "Draft" in generated artifact)
- ❌ Generator template defaults (templates should include `Status: Draft`)

### Impact

**PoC/Development:**
- **Risk Level:** Low (manual correction possible)
- **Impact:** If generator sets wrong status (e.g., "Planned"), requires manual edit

**Production:**
- **Risk Level:** Medium (quality control issue)
- **Impact:** Artifacts could bypass approval gates if generated with wrong status

### Recommended Solution

**Short-term (Current):**
- ✅ Document requirement in generate.md
- ✅ Include Status validation in Report Results
- Manual verification by operator

**Long-term:**
- Add validation check after generation: Parse metadata, verify Status = "Draft"
- Update all templates to default to `Status: Draft`
- Add automated test: Generate artifact → verify Status = "Draft"

### Implementation Priority

**Phase 1 (PoC):** Documented requirement added ✅

**Phase 2 (Production):** Medium priority - Add validation check

---

## Gap 5: Artifact Approval Workflow

### Description

Framework lacks defined process and tooling for artifact approval (marking Status from Draft → Approved).

### Current State

**What Exists:**
- Status field in artifact metadata ✅
- Critique and refinement process defined ✅

**What's Missing:**
- ❌ Approval workflow (who approves, how)
- ❌ Approval timestamp and approver tracking
- ❌ Approval checklist or criteria

### Impact

**PoC/Development:**
- **Risk Level:** Low (single operator approves informally)
- **Impact:** No audit trail for approval decisions

**Production:**
- **Risk Level:** High (governance and audit requirement)
- **Impact:** Cannot demonstrate who approved what and when; no accountability

### Recommended Solution

**Approval Process:**
1. Generator produces v1 (Draft)
2. Human critique cycle (v1 → v2 → v3)
3. Final approval decision (human judgment)
4. Update artifact metadata:
   ```markdown
   - **Status:** Approved
   - **Approved By:** [Name/Role]
   - **Approval Date:** [YYYY-MM-DD]
   - **Approval Notes:** [Brief rationale]
   ```

**Tooling:**
- Script to update artifact status with approval metadata
- Approval checklist template per artifact type
- Audit log for approval history

### Implementation Priority

**Phase 1 (PoC):** Documented gap, informal approval acceptable ✅

**Phase 2 (Production):** High priority - Required for governance and compliance

---

## Summary

| Gap | Impact (PoC) | Impact (Prod) | Priority | Status |
|-----|--------------|---------------|----------|--------|
| **Input Artifact Status Validation** | Low | High | Critical | Documented |
| **New Session Enforcement** | Low | Medium | Medium | Documented |
| **Artifact Version Tracking** | Low | Medium | Low-Med | Documented |
| **Generated Artifact Status Enforcement** | Low | Medium | Medium | Documented + Instruction Added |
| **Artifact Approval Workflow** | Low | High | High | Documented |

---

## Next Steps

**Phase 1 (PoC) - Current:**
- ✅ Document all gaps (this document)
- ✅ Update framework documentation with validation requirements
- ✅ Update TODO.md to clarify production requirements vs. current state
- ✅ Accept documented risks for PoC execution

**Phase 2 (Production Readiness):**
- ⏳ Implement input artifact status validation
- ⏳ Implement artifact approval workflow
- ⏳ Create approval checklists per artifact type
- ⏳ Add validation tests to framework test suite

**Phase 3 (Scale & Automation):**
- ⏳ Implement automated session management
- ⏳ Implement version resolution logic
- ⏳ Build orchestration tooling for validation enforcement

---

**Document Owner:** Context Engineering PoC Team
**Last Updated:** 2025-10-11
**Next Review:** End of Phase 1 or before Phase 2 production deployment

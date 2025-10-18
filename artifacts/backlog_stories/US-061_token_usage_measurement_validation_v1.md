# User Story: Token Usage Measurement and Validation

## Metadata
- **Story ID:** US-061
- **Title:** Token Usage Measurement and Validation
- **Type:** Feature
- **Status:** Backlog
- **Priority:** High - Validates primary business goal (40-60% token cost reduction), critical for ROI justification
- **Parent PRD:** PRD-006
- **Parent High-Level Story:** HLS-010
- **Functional Requirements Covered:** NFR-Performance-03 (validation via measurement)
- **Informed By Implementation Research:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

## Parent Artifact Context

**Parent PRD:** [PRD-006: MCP Server SDLC Framework Integration]
- **Link:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md`
- **PRD Section:** §Goals & Success Metrics, §Non-Functional Requirements - NFR-Performance-03, §Appendix A: Token Cost Baseline Measurement Plan
- **Functional Requirements Coverage:**
  - **NFR-Performance-03:** Token consumption for typical SDLC workflow (epic generation, PRD creation, backlog story breakdown - 10 workflows) SHALL be reduced by ≥40% vs. baseline local file approach

**Parent High-Level Story:** [HLS-010: CLAUDE.md Orchestration Update & Integration Testing]
- **Link:** `/artifacts/hls/HLS-010_claude_orchestration_integration_testing_v2.md`
- **HLS Section:** §Decomposition into Backlog Stories - Story 6

## User Story
As a Framework Maintainer, I want to measure token consumption for 10 representative workflows (local vs. MCP approach) and validate ≥40% reduction, so that the business goal of token cost reduction is empirically validated before production pilot.

## Description

The primary business justification for MCP framework migration is **40-60% token cost reduction** (per PRD-006 §Executive Summary and §Goals & Success Metrics). This reduction comes from:
1. **Optimized Resource Loading:** Load only necessary framework components (not entire CLAUDE.md every time)
2. **Resource Caching:** MCP Server caches frequently accessed resources (5-minute TTL), reducing repeated file I/O
3. **Deterministic Tools:** Replace AI inference for validation/path resolution with lightweight tool execution (no token consumption for deterministic logic)

This story implements token usage measurement instrumentation and validation process to empirically verify the 40-60% reduction target for 10 representative workflows (per PRD-006 Appendix A):

**Baseline Workflows (Local File Approach):**
1. Generate Product Vision (VIS-001) from business research
2. Generate Initiative (INIT-001) from Product Vision
3. Generate Epic (EPIC-000) from Initiative
4. Generate PRD (PRD-000) from Epic
5. Generate High-Level Story (HLS-001) from PRD
6. Generate Backlog Story (US-001) from HLS + PRD
7. Generate Tech Spec (SPEC-001) from Backlog Story
8. Refine Epic (EPIC-000 v1 → v2) based on critique
9. Refine PRD (PRD-000 v1 → v2) based on critique
10. Validate PRD-000 against 26-criterion checklist

**Measurement Method:**
- **Baseline:** Execute each workflow with local file approach (`use_mcp_framework: false`), record token usage from Claude API telemetry
- **MCP Approach:** Execute same workflows with MCP approach (`use_mcp_framework: true`), record token usage
- **Comparison:** Calculate % reduction per workflow and aggregate average
- **Target:** ≥40% aggregate reduction (per NFR-Performance-03)

**Scope:**
- In Scope: Token usage measurement instrumentation (telemetry capture)
- In Scope: Baseline measurement (local file approach for 10 workflows)
- In Scope: MCP measurement (MCP approach for 10 workflows)
- In Scope: Comparison analysis and validation report
- Out of Scope: Integration testing (covered by US-060)
- Out of Scope: Performance benchmarking for latency (covered by HLS-011 production readiness)

## Implementation Research References

**Primary Research Document:** /artifacts/research/AI_Agent_MCP_Server_implementation_research.md

**Technical Patterns Applied:**
- **§8.1: Token Optimization Patterns:** Reducing CLAUDE.md from 800+ lines to ~200 lines saves ~15-20k tokens per load
  - **Example:** Baseline loads full CLAUDE.md (800 lines ≈ 20k tokens), MCP loads orchestrator only (200 lines ≈ 5k tokens)
- **§8.10: Telemetry Instrumentation:** Use Claude API response headers for token usage data (input_tokens, output_tokens, cache_read_tokens)
  - **Data Source:** Claude API returns token counts in response metadata
- **§8.11: Measurement Isolation:** Run workflows independently to isolate token usage per workflow (no shared context contamination)

**Anti-Patterns Avoided:**
- **§6.10: Assumed Performance Improvements:** Avoid assuming 40-60% reduction without empirical measurement (validate business goals with data)
- **§6.11: Single Workflow Measurement:** Avoid measuring only one workflow (not representative of typical usage patterns)

**Performance Considerations:**
- **§8.12: Measurement Overhead:** Token measurement adds minimal overhead (read API response headers, log to CSV)
- **§8.13: Baseline Repeatability:** Run each workflow 3 times (baseline and MCP), use median token count to reduce variance

## Functional Requirements
- Implement token usage measurement instrumentation (capture input_tokens, output_tokens, cache_read_tokens from Claude API)
- Execute 10 baseline workflows with local file approach (`use_mcp_framework: false`)
- Execute 10 MCP workflows with MCP approach (`use_mcp_framework: true`)
- Record token usage for each workflow execution (3 runs per workflow, use median)
- Calculate % reduction per workflow and aggregate average
- Validate aggregate reduction ≥40% (NFR-Performance-03 target)
- Generate token usage comparison report (CSV and markdown summary)
- Document measurement methodology and results

## Non-Functional Requirements
- **Accuracy:** Token counts captured from official Claude API telemetry (not estimated)
- **Repeatability:** Run each workflow 3 times, use median to reduce variance (coefficient of variation <10%)
- **Transparency:** Token usage data logged to CSV for auditing and future comparison
- **Documentation:** Measurement methodology documented, results published in validation report

## Technical Requirements

**HYBRID CLAUDE.md APPROACH:** This story implements token usage measurement, not framework changes.

### Implementation Guidance

**Step 1: Token Usage Instrumentation**

Implement telemetry capture for Claude API calls:

```python
# src/telemetry/token_tracker.py

import csv
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime

@dataclass
class TokenUsage:
    workflow_id: str
    approach: str  # "local" or "mcp"
    run_number: int
    input_tokens: int
    output_tokens: int
    cache_read_tokens: int
    total_tokens: int
    timestamp: datetime

class TokenTracker:
    """Track token usage for workflow executions"""

    def __init__(self, output_file: Path):
        self.output_file = output_file
        self.measurements: list[TokenUsage] = []

    def record(self, workflow_id: str, approach: str, run_number: int,
               input_tokens: int, output_tokens: int, cache_read_tokens: int = 0):
        """Record token usage for a workflow execution"""
        total_tokens = input_tokens + output_tokens
        measurement = TokenUsage(
            workflow_id=workflow_id,
            approach=approach,
            run_number=run_number,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cache_read_tokens=cache_read_tokens,
            total_tokens=total_tokens,
            timestamp=datetime.now()
        )
        self.measurements.append(measurement)

    def save_to_csv(self):
        """Save measurements to CSV file"""
        with open(self.output_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "workflow_id", "approach", "run_number",
                "input_tokens", "output_tokens", "cache_read_tokens",
                "total_tokens", "timestamp"
            ])
            for m in self.measurements:
                writer.writerow([
                    m.workflow_id, m.approach, m.run_number,
                    m.input_tokens, m.output_tokens, m.cache_read_tokens,
                    m.total_tokens, m.timestamp.isoformat()
                ])

    def calculate_reduction(self) -> dict:
        """Calculate token reduction per workflow and aggregate average"""
        results = {}
        workflows = set(m.workflow_id for m in self.measurements)

        for workflow_id in workflows:
            local_runs = [m.total_tokens for m in self.measurements
                          if m.workflow_id == workflow_id and m.approach == "local"]
            mcp_runs = [m.total_tokens for m in self.measurements
                        if m.workflow_id == workflow_id and m.approach == "mcp"]

            if not local_runs or not mcp_runs:
                continue

            # Use median to reduce variance
            local_median = sorted(local_runs)[len(local_runs) // 2]
            mcp_median = sorted(mcp_runs)[len(mcp_runs) // 2]

            reduction_pct = ((local_median - mcp_median) / local_median) * 100
            results[workflow_id] = {
                "local_median": local_median,
                "mcp_median": mcp_median,
                "reduction_pct": reduction_pct
            }

        # Calculate aggregate average reduction
        if results:
            avg_reduction = sum(r["reduction_pct"] for r in results.values()) / len(results)
            results["aggregate"] = {
                "average_reduction_pct": avg_reduction,
                "target_met": avg_reduction >= 40.0
            }

        return results
```

**Step 2: Workflow Execution Harness**

Create test harness for executing workflows with token tracking:

```python
# tests/performance/test_token_usage.py

import pytest
from pathlib import Path
from telemetry.token_tracker import TokenTracker

# Workflow definitions (per PRD-006 Appendix A)
WORKFLOWS = [
    {"id": "WF-01", "name": "Generate Product Vision (VIS-001)"},
    {"id": "WF-02", "name": "Generate Initiative (INIT-001)"},
    {"id": "WF-03", "name": "Generate Epic (EPIC-000)"},
    {"id": "WF-04", "name": "Generate PRD (PRD-000)"},
    {"id": "WF-05", "name": "Generate High-Level Story (HLS-001)"},
    {"id": "WF-06", "name": "Generate Backlog Story (US-001)"},
    {"id": "WF-07", "name": "Generate Tech Spec (SPEC-001)"},
    {"id": "WF-08", "name": "Refine Epic (EPIC-000 v1 → v2)"},
    {"id": "WF-09", "name": "Refine PRD (PRD-000 v1 → v2)"},
    {"id": "WF-10", "name": "Validate PRD-000 (26-criterion checklist)"},
]

@pytest.fixture(scope="session")
def token_tracker():
    """Initialize token tracker for session"""
    tracker = TokenTracker(output_file=Path("token_usage_report.csv"))
    yield tracker
    # Save results at end of session
    tracker.save_to_csv()

@pytest.mark.parametrize("workflow", WORKFLOWS)
def test_token_usage_local_approach(workflow, token_tracker):
    """Execute workflow with local file approach and track token usage"""
    for run in range(1, 4):  # 3 runs per workflow
        # Setup: Configure local file mode
        config = {"use_mcp_framework": False}

        # Execute: Run workflow (simulated - actual test would invoke Claude Code)
        # Capture token usage from Claude API response
        response = execute_workflow_local(workflow["id"], config)

        # Record: Log token usage
        token_tracker.record(
            workflow_id=workflow["id"],
            approach="local",
            run_number=run,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens
        )

@pytest.mark.parametrize("workflow", WORKFLOWS)
def test_token_usage_mcp_approach(workflow, token_tracker):
    """Execute workflow with MCP approach and track token usage"""
    for run in range(1, 4):  # 3 runs per workflow
        # Setup: Configure MCP mode
        config = {"use_mcp_framework": True, "mcp_server_url": "http://localhost:3000"}

        # Execute: Run workflow
        response = execute_workflow_mcp(workflow["id"], config)

        # Record: Log token usage
        token_tracker.record(
            workflow_id=workflow["id"],
            approach="mcp",
            run_number=run,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            cache_read_tokens=response.cache_read_tokens  # MCP Server may use cache
        )
```

**Step 3: Generate Token Usage Report**

Generate comparison report after measurement:

```python
# scripts/generate_token_report.py

from telemetry.token_tracker import TokenTracker
from pathlib import Path

def generate_report():
    tracker = TokenTracker.load_from_csv(Path("token_usage_report.csv"))
    results = tracker.calculate_reduction()

    # Generate Markdown report
    report = ["# Token Usage Comparison Report\n"]
    report.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}\n")
    report.append(f"**Measurement Method:** 10 workflows × 3 runs (median used)\n\n")
    report.append("## Per-Workflow Results\n\n")
    report.append("| Workflow | Local (Median) | MCP (Median) | Reduction % |\n")
    report.append("|----------|----------------|--------------|-------------|\n")

    for workflow_id in sorted([k for k in results.keys() if k != "aggregate"]):
        r = results[workflow_id]
        report.append(f"| {workflow_id} | {r['local_median']:,} | {r['mcp_median']:,} | {r['reduction_pct']:.1f}% |\n")

    report.append("\n## Aggregate Results\n\n")
    agg = results["aggregate"]
    report.append(f"- **Average Reduction:** {agg['average_reduction_pct']:.1f}%\n")
    report.append(f"- **Target (NFR-Performance-03):** ≥40%\n")
    report.append(f"- **Target Met:** {'✅ YES' if agg['target_met'] else '❌ NO'}\n")

    # Save report
    Path("token_usage_report.md").write_text("".join(report))
    print("Report saved to token_usage_report.md")

if __name__ == "__main__":
    generate_report()
```

**Step 4: Measurement Execution**

Execute measurement process:

```bash
# Start MCP Server and Task Tracking microservice
task mcp-server-start
task task-tracking-start

# Run token usage tests (baseline: local approach)
pytest tests/performance/test_token_usage.py::test_token_usage_local_approach -v

# Run token usage tests (MCP approach)
pytest tests/performance/test_token_usage.py::test_token_usage_mcp_approach -v

# Generate comparison report
python scripts/generate_token_report.py

# Review results
cat token_usage_report.md
```

**Step 5: Validation**

- Verify token counts captured from Claude API telemetry (not estimated)
- Verify 3 runs per workflow, median used for comparison
- Verify aggregate reduction ≥40% (NFR-Performance-03 target)
- Document measurement methodology and results in validation report

**References to Implementation Standards:**
- patterns-testing.md: Follow testing patterns (pytest fixtures, test data management)
- patterns-tooling.md: Use Taskfile commands for measurement execution

### Technical Tasks
- [ ] Implement TokenTracker class for telemetry capture
- [ ] Implement workflow execution harness (local and MCP modes)
- [ ] Create 10 workflow test definitions (per PRD-006 Appendix A)
- [ ] Execute baseline measurement (local file approach, 3 runs per workflow)
- [ ] Execute MCP measurement (MCP approach, 3 runs per workflow)
- [ ] Implement token usage comparison analysis (calculate % reduction)
- [ ] Generate token usage comparison report (CSV and markdown)
- [ ] Validate aggregate reduction ≥40% (NFR-Performance-03)
- [ ] Document measurement methodology
- [ ] Publish validation report

## Acceptance Criteria

### Scenario 1: Token Usage Captured for All Workflows
**Given** 10 workflows executed with local file approach (3 runs each)
**When** token usage instrumentation executes
**Then** token counts (input, output, total) captured for all 30 executions (10 workflows × 3 runs)

### Scenario 2: Token Usage Captured for MCP Workflows
**Given** 10 workflows executed with MCP approach (3 runs each)
**When** token usage instrumentation executes
**Then** token counts (input, output, cache_read, total) captured for all 30 executions

### Scenario 3: Median Calculation Per Workflow
**Given** 3 runs per workflow recorded
**When** token usage analysis executes
**Then** median token count calculated per workflow (local and MCP) to reduce variance

### Scenario 4: Aggregate Reduction ≥40%
**Given** token usage data for all 10 workflows (local vs. MCP)
**When** aggregate reduction calculated
**Then** average reduction across all workflows ≥40% (NFR-Performance-03 target met)

### Scenario 5: Token Usage Report Generated
**Given** token usage measurements complete
**When** report generation script executes
**Then** markdown report generated with per-workflow results, aggregate reduction, and target validation (✅ YES or ❌ NO)

## Implementation Tasks Evaluation

**Purpose:** Determine if this backlog story should be decomposed into separate Implementation Tasks (TASK-XXX artifacts) per SDLC Guideline v1.3 Section 11.

**Decision:** No Tasks Needed

**Rationale:**
- **Story Points:** 3 SP (CONSIDER threshold, below DON'T SKIP at 8+ SP)
- **Developer Count:** Single developer (measurement automation focused)
- **Domain Span:** Single domain (testing/telemetry only, no production code changes)
- **Complexity:** Medium - Straightforward instrumentation and measurement, clear methodology
- **Uncertainty:** Low - Token counts available from Claude API telemetry, measurement process well-defined
- **Override Factors:** None - No cross-domain dependencies, no security-critical changes, no unfamiliar technology

**Conclusion:** While 3 SP is at CONSIDER threshold, the focused nature of the work (telemetry instrumentation, measurement automation) with clear methodology does not warrant task decomposition. Implementation can proceed as a single cohesive unit of work within one sprint.

## Definition of Done
- [ ] TokenTracker class implemented for telemetry capture
- [ ] Workflow execution harness implemented (local and MCP modes)
- [ ] 10 workflow test definitions created (per PRD-006 Appendix A)
- [ ] Baseline measurement executed (local file approach, 3 runs per workflow)
- [ ] MCP measurement executed (MCP approach, 3 runs per workflow)
- [ ] Token usage comparison analysis implemented (calculate % reduction)
- [ ] Token usage comparison report generated (CSV and markdown)
- [ ] Aggregate reduction ≥40% validated (NFR-Performance-03)
- [ ] Measurement methodology documented
- [ ] Validation report published
- [ ] Code reviewed and approved
- [ ] Product Owner acceptance obtained

## Additional Information
**Suggested Labels:** performance, testing, telemetry, validation
**Estimated Story Points:** 3
**Dependencies:**
- **Depends On:** US-056/057/058/059 (CLAUDE.md Orchestration) - both modes (local and MCP) required for comparison
- **Depends On:** US-060 (Integration Testing) - workflow execution patterns reused for measurement
- **Related:** HLS-011 (Production Readiness) - token cost validation critical for production pilot justification

## Open Questions & Implementation Uncertainties

**No open implementation questions. All technical approaches clear from PRD-006 v3 §Goals & Success Metrics and §Appendix A: Token Cost Baseline Measurement Plan.**

**Key Decisions Already Made:**
- Workflows to measure: 10 workflows defined in PRD-006 Appendix A
- Measurement method: Claude API telemetry (input_tokens, output_tokens, cache_read_tokens)
- Runs per workflow: 3 runs, use median to reduce variance
- Target: ≥40% aggregate reduction (NFR-Performance-03)
- Comparison metric: % reduction per workflow, aggregate average across all workflows

## Related Documents
- **Parent PRD:** `/artifacts/prds/PRD-006_mcp_server_sdlc_framework_integration_v3.md` (§Appendix A: Token Cost Baseline Measurement Plan)
- **Parent HLS:** `/artifacts/hls/HLS-010_claude_orchestration_integration_testing_v2.md`
- **Parent Epic:** `/artifacts/epics/EPIC-006_mcp_server_sdlc_framework_integration_v2.md`
- **Implementation Research:** `/artifacts/research/AI_Agent_MCP_Server_implementation_research.md`
- **Related Stories:** US-060 (Integration Testing), US-062 (Regression Testing), HLS-011 (Production Readiness)

## Version History
- **v1 (2025-10-18):** Initial version

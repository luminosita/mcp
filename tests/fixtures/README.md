# Test Fixtures for Generator Integration Tests

This directory contains test fixtures for US-037 integration tests.

## Directory Structure

```
fixtures/
├── artifacts/           # Sample input artifacts for generator tests
│   ├── epic/           # Epic artifacts for prd-generator tests
│   ├── prd/            # PRD artifacts for hls-generator tests
│   └── ...
└── expected_outputs/    # Expected output artifacts for byte-identical comparison
    ├── prd/            # Expected PRD outputs
    ├── hls/            # Expected HLS outputs
    └── ...
```

## Usage

### Adding Test Data for New Generator

To add test data for a new generator type:

1. **Create input artifact directory:**
   ```bash
   mkdir -p tests/fixtures/artifacts/{generator-type}
   ```

2. **Add sample input artifact:**
   ```bash
   cp artifacts/{type}/{sample-artifact}.md tests/fixtures/artifacts/{generator-type}/
   ```

3. **Add expected output (optional):**
   ```bash
   mkdir -p tests/fixtures/expected_outputs/{generator-type}
   # Generate expected output and save to expected_outputs/
   ```

4. **Update test parameters:**
   - Add generator name to `ALL_GENERATORS` list in `test_generator_byte_identity.py`
   - Parameterized tests automatically include new generator

### Example: Adding deployment-plan Generator

```bash
# 1. Create directories
mkdir -p tests/fixtures/artifacts/deployment-plan
mkdir -p tests/fixtures/expected_outputs/deployment-plan

# 2. Add sample input (e.g., tech spec artifact)
cp artifacts/tech_specs/SPEC-001_*.md tests/fixtures/artifacts/deployment-plan/input.md

# 3. Generate expected output (manual or via generator)
# Save to tests/fixtures/expected_outputs/deployment-plan/expected.md

# 4. Update test
# Add "deployment-plan" to ALL_GENERATORS list in test_generator_byte_identity.py
```

## Test Scenarios Covered

### Scenario 1: Byte-Identical Comparison
- Input: Sample artifact from `artifacts/`
- Test: Generate via MCP vs. local file
- Validation: MD5 hash comparison

### Scenario 2: Performance Benchmarks
- Test: Load generator 100+ times
- Metrics: p50, p95, p99 latencies
- Target: p95 <500ms (US-037 NFR-Performance-02)

### Scenario 3-8: Error Scenarios, CI/CD, Reporting
- See `test_generator_byte_identity.py` for details

## Current Test Coverage

| Generator Type | Input Fixture | Expected Output | Status |
|---------------|---------------|-----------------|--------|
| product-vision | N/A | N/A | ✅ Prompt loading tested |
| initiative | N/A | N/A | ✅ Prompt loading tested |
| epic | N/A | N/A | ✅ Prompt loading tested |
| prd | N/A | N/A | ✅ Prompt loading tested |
| high-level-user-story | N/A | N/A | ✅ Prompt loading tested |
| backlog-story | N/A | N/A | ✅ Prompt loading tested |
| spike | N/A | N/A | ✅ Prompt loading tested |
| adr | N/A | N/A | ✅ Prompt loading tested |
| tech-spec | N/A | N/A | ✅ Prompt loading tested |
| implementation-task | N/A | N/A | ✅ Prompt loading tested |

**Note:** Full artifact generation tests require LLM integration. Current tests validate:
- ✅ Prompt loading (MCP vs local file byte-identical)
- ✅ Performance metrics (p50, p95, p99 latencies)
- ✅ Error handling (missing prompt, path traversal)
- ⏳ Full artifact generation (requires LLM mock or integration)

## Future Enhancements

1. **Add Mock LLM Responses:**
   - Mock Claude API responses for deterministic artifact generation
   - Enable full byte-identical artifact comparison without API calls

2. **Add Sample Input Artifacts:**
   - Representative artifacts for each generator type
   - Enable end-to-end generator execution tests

3. **Add CI/CD Performance Baselines:**
   - Store baseline metrics for comparison
   - Detect performance regressions in CI/CD

## Related Documents

- **US-037:** `/artifacts/backlog_stories/US-037_integration_testing_all_generator_types_v1.md`
- **Test Implementation:** `/tests/integration/test_generator_byte_identity.py`
- **CLAUDE.md Testing Patterns:** `/prompts/CLAUDE/python/CLAUDE-testing.md`

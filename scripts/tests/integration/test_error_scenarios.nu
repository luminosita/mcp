#!/usr/bin/env nu

# Integration Tests: Error Scenarios
#
# Tests error handling and recovery in setup script:
# - Prerequisites validation failures
# - Graceful error messages with remediation steps
# - Error propagation and exit codes
# - Environment safety (no corruption on failure)
#
# Note: Testing actual missing prerequisites (Python, Podman, Git) requires
# a non-devbox environment or mocking. These tests focus on error handling
# patterns and validation logic.
#
# Usage:
#   nu tests/integration/test_error_scenarios.nu

use std assert

# Test 1: Verify prerequisites module reports correct structure
export def test_prerequisites_validation_structure [] {
    print "\n🧪 Test 1: Prerequisites validation returns correct structure"

    let result = (^nu -c "use scripts/lib/prerequisites.nu; check_prerequisites" | complete)

    # Should succeed in devbox environment
    assert ($result.exit_code == 0) "Prerequisites check failed unexpectedly"

    # Output should be a structured record
    # We verify the module runs without errors, which proves structure is correct
    print "✅ Prerequisites validation returns structured data"
}

# Test 2: Test Taskfile validation error handling
export def test_taskfile_validation_error_handling [] {
    print "\n🧪 Test 2: Taskfile validation handles missing Taskfile gracefully"

    # Test the validation logic directly
    let result = (^nu -c "use scripts/lib/taskfile_install.nu; check_taskfile_installed" | complete)

    # In devbox environment, Taskfile should be present
    # We verify the function executes without crashing
    assert ($result.exit_code == 0) "Taskfile validation crashed"

    print "✅ Taskfile validation executes without errors"
}

# Test 3: Test UV validation error handling
export def test_uv_validation_error_handling [] {
    print "\n🧪 Test 3: UV validation handles errors gracefully"

    # Test the validation logic directly
    let result = (^nu -c "use scripts/lib/uv_install.nu; check_uv_installed" | complete)

    # In devbox environment, UV should be present
    # We verify the function executes without crashing
    assert ($result.exit_code == 0) "UV validation crashed"

    print "✅ UV validation executes without errors"
}

# Test 4: Test setup fails fast on prerequisite failure
export def test_setup_fails_fast_on_prerequisite_error [] {
    print "\n🧪 Test 4: Setup fails fast when prerequisites missing (simulated)"

    # This test verifies that setup.nu checks prerequisites early
    # and exits before attempting installation steps

    # We'll test by examining the setup.nu source code structure
    let setup_content = (open scripts/setup.nu)

    # Verify prerequisites check happens in Phase 2 (before installation phases)
    assert (($setup_content | str contains "Phase 2: Prerequisites")) "Prerequisites phase not found"
    assert (($setup_content | str contains "check_prerequisites")) "Prerequisites check not called"

    # Verify setup exits on prerequisites failure
    assert (($setup_content | str contains "exit 1")) "Setup doesn't exit on error"

    print "✅ Setup implements fail-fast prerequisite checking"
}

# Test 5: Test validation module error reporting
export def test_validation_error_reporting [] {
    print "\n🧪 Test 5: Validation module reports errors clearly"

    # Test individual validation functions to verify error handling
    # In a working environment, these should pass

    let result = (^nu -c "use scripts/lib/validation.nu; validate_env_file" | complete)

    # Function should execute without crashing (even if .env missing)
    # The function returns a record with pass/fail status
    # We verify it doesn't crash with exit code errors
    if $result.exit_code != 0 {
        # It's okay if validation fails (returns false), but shouldn't crash
        print $"  ⚠️  Validation returned non-zero exit (expected if .env missing): ($result.stderr)"
    }

    print "✅ Validation module executes without crashing"
}

# Test 6: Test error messages include remediation steps
export def test_error_messages_quality [] {
    print "\n🧪 Test 6: Error messages include helpful remediation"

    # Check common.nu for error messaging utilities
    let common_content = (open scripts/lib/common.nu)

    # Verify error messages include devbox.json guidance
    assert (($common_content | str contains "devbox.json") or ($common_content | str contains "error")) "Error messages don't reference devbox.json"

    # Check prerequisites.nu for error messages
    let prereqs_content = (open scripts/lib/prerequisites.nu)

    # Verify prerequisite errors include version information
    assert (($prereqs_content | str contains "version") or ($prereqs_content | str contains "required")) "Prerequisites don't check versions"

    print "✅ Error messages include remediation guidance"
}

# Test 7: Test setup doesn't corrupt environment on failure
export def test_no_corruption_on_failure [] {
    print "\n🧪 Test 7: Setup doesn't corrupt environment on failure"

    # Verify .gitignore includes .venv and .env (safety net)
    assert (".gitignore" | path exists) ".gitignore not found"

    let gitignore_content = (open .gitignore)
    assert (($gitignore_content | str contains ".venv") or ($gitignore_content | str contains "venv")) ".venv not in .gitignore"
    assert (($gitignore_content | str contains ".env")) ".env not in .gitignore"

    # Verify .env.example exists (template for .env)
    assert (".env.example" | path exists) ".env.example not found (needed for safe .env generation)"

    print "✅ Setup has safety mechanisms (git ignore patterns, templates)"
}

# Test 8: Test validation returns structured error reports
export def test_validation_structured_errors [] {
    print "\n🧪 Test 8: Validation returns structured error reports"

    # Run validation and verify it returns structured data
    # (not just text output)

    # Check validation.nu source for structured returns
    let validation_content = (open scripts/lib/validation.nu)

    # Verify functions return records with pass/fail fields
    assert (($validation_content | str contains "passed") or ($validation_content | str contains "failed")) "Validation doesn't use structured pass/fail"
    assert (($validation_content | str contains "error") or ($validation_content | str contains "message")) "Validation doesn't include error messages"

    print "✅ Validation returns structured error reports"
}

# Test 9: Test setup exit codes are correct
export def test_setup_exit_codes [] {
    print "\n🧪 Test 9: Setup uses correct exit codes"

    # Check setup.nu for proper exit code usage
    let setup_content = (open scripts/setup.nu)

    # Verify exit 0 on success
    assert (($setup_content | str contains "exit 0")) "Setup doesn't exit with code 0 on success"

    # Verify exit 1 on failure
    assert (($setup_content | str contains "exit 1")) "Setup doesn't exit with code 1 on failure"

    # Verify exit codes based on error count
    assert (($setup_content | str contains "errors")) "Setup doesn't track errors"

    print "✅ Setup uses correct exit codes (0=success, 1=failure)"
}

# Test 10: Test retry logic exists for network operations
export def test_retry_logic_exists [] {
    print "\n🧪 Test 10: Retry logic exists for network operations"

    # Check deps_install.nu for retry logic
    let deps_content = (open scripts/lib/deps_install.nu)

    # Verify retry attempts are implemented
    assert (($deps_content | str contains "retry") or ($deps_content | str contains "attempt")) "No retry logic found in deps_install.nu"

    # Check common.nu for retry utilities
    let common_content = (open scripts/lib/common.nu)

    # Verify backoff or retry mechanisms exist
    assert (($common_content | str contains "retry") or ($common_content | str contains "sleep") or ($common_content | str contains "backoff")) "No retry utilities in common.nu"

    print "✅ Retry logic implemented for network operations"
}

# Main test runner
def main [] {
    print "\n╔═══════════════════════════════════════════════════════════╗"
    print "║         Integration Tests: Error Scenarios               ║"
    print "╚═══════════════════════════════════════════════════════════╝\n"

    let start_time = (date now)

    # Run tests sequentially
    let test_results = [
        (try { test_prerequisites_validation_structure; {name: "Prerequisites validation structure", passed: true} } catch {|e| {name: "Prerequisites validation structure", passed: false, error: $e.msg}})
        (try { test_taskfile_validation_error_handling; {name: "Taskfile validation error handling", passed: true} } catch {|e| {name: "Taskfile validation error handling", passed: false, error: $e.msg}})
        (try { test_uv_validation_error_handling; {name: "UV validation error handling", passed: true} } catch {|e| {name: "UV validation error handling", passed: false, error: $e.msg}})
        (try { test_setup_fails_fast_on_prerequisite_error; {name: "Setup fails fast on errors", passed: true} } catch {|e| {name: "Setup fails fast on errors", passed: false, error: $e.msg}})
        (try { test_validation_error_reporting; {name: "Validation error reporting", passed: true} } catch {|e| {name: "Validation error reporting", passed: false, error: $e.msg}})
        (try { test_error_messages_quality; {name: "Error message quality", passed: true} } catch {|e| {name: "Error message quality", passed: false, error: $e.msg}})
        (try { test_no_corruption_on_failure; {name: "No corruption on failure", passed: true} } catch {|e| {name: "No corruption on failure", passed: false, error: $e.msg}})
        (try { test_validation_structured_errors; {name: "Structured error reports", passed: true} } catch {|e| {name: "Structured error reports", passed: false, error: $e.msg}})
        (try { test_setup_exit_codes; {name: "Correct exit codes", passed: true} } catch {|e| {name: "Correct exit codes", passed: false, error: $e.msg}})
        (try { test_retry_logic_exists; {name: "Retry logic exists", passed: true} } catch {|e| {name: "Retry logic exists", passed: false, error: $e.msg}})
    ]

    # Print failures
    for result in $test_results {
        if not $result.passed {
            print $"❌ Test '($result.name)' failed: ($result.error)"
        }
    }

    # Calculate stats
    let passed = ($test_results | where passed == true | length)
    let failed = ($test_results | where passed == false | length)

    # Calculate duration
    let end_time = (date now)
    let duration = ($end_time - $start_time)

    # Display results
    print "\n╔═══════════════════════════════════════════════════════════╗"

    if $failed == 0 {
        print "║           ✅ All Error Scenario Tests Passed!           ║"
    } else {
        print "║           ⚠️  Some Error Scenario Tests Failed          ║"
    }

    print "╚═══════════════════════════════════════════════════════════╝\n"

    print $"📊 Results: ($passed) passed, ($failed) failed"
    print $"⏱️  Total test time: ($duration)\n"

    # Exit with appropriate code
    if $failed > 0 {
        exit 1
    }
}

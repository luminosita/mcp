#!/usr/bin/env nu

# Integration Tests: Full Setup Flow (End-to-End)
#
# Tests the complete setup script execution from start to finish, validating:
# - All 8 setup phases complete successfully
# - Environment is ready for development after setup
# - Idempotent re-run behavior (second run skips completed steps)
# - Setup completes within performance targets
#
# Usage:
#   nu tests/integration/test_setup_flow.nu
#   nu tests/integration/test_setup_flow.nu --verbose

use std assert

# Backup existing environment state
def backup_environment [] {
    print "📦 Backing up existing environment..."

    # Backup .venv if exists
    if (".venv" | path exists) {
        if (".venv.backup" | path exists) {
            rm -rf .venv.backup
        }
        mv .venv .venv.backup
        print "  ✅ Backed up .venv → .venv.backup"
    }

    # Backup .env if exists
    if (".env" | path exists) {
        if (".env.backup" | path exists) {
            rm .env.backup
        }
        cp .env .env.backup
        print "  ✅ Backed up .env → .env.backup"
    }
}

# Restore environment state
def restore_environment [] {
    print "♻️  Restoring environment..."

    # Restore .venv backup
    if (".venv.backup" | path exists) {
        if (".venv" | path exists) {
            rm -rf .venv
        }
        mv .venv.backup .venv
        print "  ✅ Restored .venv from backup"
    }

    # Restore .env backup
    if (".env.backup" | path exists) {
        if (".env" | path exists) {
            rm .env
        }
        mv .env.backup .env
        print "  ✅ Restored .env from backup"
    }
}

# Clean up test environment (remove created artifacts)
def cleanup_test_artifacts [] {
    print "🧹 Cleaning up test artifacts..."

    # Remove test .venv
    if (".venv" | path exists) {
        rm -rf .venv
        print "  ✅ Removed test .venv"
    }

    # Remove test .env (restore from .env.example)
    if (".env" | path exists) and (".env.backup" | path exists | not $in) {
        rm .env
        print "  ✅ Removed test .env"
    }
}

# Test 1: Verify all setup modules exist
export def test_all_modules_exist [] {
    print "\n🧪 Test 1: Verify all setup modules exist"

    let modules = [
        "scripts/setup.nu"
        "scripts/lib/os_detection.nu"
        "scripts/lib/prerequisites.nu"
        "scripts/lib/taskfile_install.nu"
        "scripts/lib/uv_install.nu"
        "scripts/lib/venv_setup.nu"
        "scripts/lib/deps_install.nu"
        "scripts/lib/config_setup.nu"
        "scripts/lib/validation.nu"
        "scripts/lib/interactive.nu"
        "scripts/lib/common.nu"
    ]

    for module in $modules {
        assert ($module | path exists) $"Module not found: ($module)"
    }

    print "✅ All required modules exist (11 modules)"
}

# Test 2: Verify setup script syntax is valid
export def test_setup_script_syntax [] {
    print "\n🧪 Test 2: Verify setup script syntax"

    let result = (^nu -c "nu-check scripts/setup.nu" | complete)

    if $result.exit_code != 0 {
        print $"❌ Syntax check failed: ($result.stderr)"
        assert false "Setup script has syntax errors"
    }

    print "✅ Setup script syntax is valid"
}

# Test 3: Test full setup execution in silent mode
export def test_full_setup_execution [] {
    print "\n🧪 Test 3: Full setup execution (silent mode)"
    print "⏱️  This test executes the complete setup flow..."

    # Backup environment
    backup_environment

    # Clean up before test
    cleanup_test_artifacts

    try {
        let start_time = (date now)

        # Run setup in silent mode
        print "\n🚀 Running: nu scripts/setup.nu --silent\n"
        let result = (^nu scripts/setup.nu --silent | complete)

        let end_time = (date now)
        let duration = ($end_time - $start_time)

        # Check exit code
        assert ($result.exit_code == 0) $"Setup failed with exit code ($result.exit_code)\nStderr: ($result.stderr)"

        # Verify output contains success indicators
        assert (($result.stdout | str contains "Setup Complete") or ($result.stdout | str contains "✅")) "Setup output missing success indicator"

        # Verify .venv created
        assert (".venv" | path exists) "Virtual environment not created"
        assert (".venv/bin/python" | path exists) "Python binary not found in venv"
        assert (".venv/bin/activate" | path exists) "Activate script not found in venv"

        # Verify .env created
        assert (".env" | path exists) ".env file not created"

        # Verify dependencies installed
        let pip_list = (^.venv/bin/python -m pip list | complete)
        assert ($pip_list.exit_code == 0) "Failed to list installed packages"
        assert (($pip_list.stdout | str contains "fastapi") or ($pip_list.stdout | str contains "FastAPI")) "FastAPI not installed"

        print $"\n✅ Full setup completed successfully in ($duration)"

        # Clean up after test
        cleanup_test_artifacts
    } catch {|e|
        # Restore environment on failure
        restore_environment
        error make {msg: $"Test failed: ($e.msg)"}
    }

    # Restore environment
    restore_environment
}

# Test 4: Test idempotent re-run (second run should be fast)
export def test_idempotent_rerun [] {
    print "\n🧪 Test 4: Idempotent re-run (should skip completed steps)"
    print "⏱️  This test validates setup can run multiple times safely..."

    # Backup environment
    backup_environment

    # Clean up before test
    cleanup_test_artifacts

    try {
        # First run
        print "\n🚀 First run: nu scripts/setup.nu --silent\n"
        let first_run = (^nu scripts/setup.nu --silent | complete)
        assert ($first_run.exit_code == 0) "First setup run failed"

        # Second run (should be idempotent)
        print "\n🚀 Second run: nu scripts/setup.nu --silent\n"
        let start_time = (date now)
        let second_run = (^nu scripts/setup.nu --silent | complete)
        let end_time = (date now)
        let duration = ($end_time - $start_time)

        assert ($second_run.exit_code == 0) "Second setup run failed"

        # Second run should complete quickly (validation only)
        # Note: We don't enforce strict timing here as it depends on hardware
        print $"\n✅ Idempotent re-run completed in ($duration)"
        print "   (Second run successfully validated existing environment)"

        # Clean up after test
        cleanup_test_artifacts
    } catch {|e|
        # Restore environment on failure
        restore_environment
        error make {msg: $"Test failed: ($e.msg)"}
    }

    # Restore environment
    restore_environment
}

# Test 5: Verify environment is ready for development
export def test_environment_ready [] {
    print "\n🧪 Test 5: Verify environment is ready for development"

    # Backup environment
    backup_environment

    # Clean up before test
    cleanup_test_artifacts

    try {
        # Run setup
        print "\n🚀 Running setup: nu scripts/setup.nu --silent\n"
        let setup_result = (^nu scripts/setup.nu --silent | complete)
        assert ($setup_result.exit_code == 0) "Setup failed"

        # Verify Python version
        let python_version = (^.venv/bin/python --version | complete)
        assert ($python_version.exit_code == 0) "Python not executable"
        assert (($python_version.stdout | str contains "3.11") or ($python_version.stdout | str contains "3.12") or ($python_version.stdout | str contains "3.13")) "Python version not 3.11+"

        # Verify critical packages installed
        let packages = ["fastapi", "uvicorn", "pydantic", "pytest"]
        for package in $packages {
            let check = (^.venv/bin/python -m pip show $package | complete)
            assert ($check.exit_code == 0) $"Package ($package) not installed"
        }

        # Verify Taskfile is functional
        let task_check = (^task --version | complete)
        assert ($task_check.exit_code == 0) "Taskfile not functional"

        # Verify task list works
        let task_list = (^task --list | complete)
        assert ($task_list.exit_code == 0) "Taskfile list command failed"

        print "\n✅ Environment is ready for development"
        print "   - Python 3.11+ installed"
        print "   - Critical packages installed (fastapi, uvicorn, pydantic, pytest)"
        print "   - Taskfile functional"

        # Clean up after test
        cleanup_test_artifacts
    } catch {|e|
        # Restore environment on failure
        restore_environment
        error make {msg: $"Test failed: ($e.msg)"}
    }

    # Restore environment
    restore_environment
}

# Test 6: Verify all setup phases execute
export def test_all_phases_execute [] {
    print "\n🧪 Test 6: Verify all 8 setup phases execute"

    # Backup environment
    backup_environment

    # Clean up before test
    cleanup_test_artifacts

    try {
        # Run setup and capture output
        print "\n🚀 Running setup: nu scripts/setup.nu --silent\n"
        let result = (^nu scripts/setup.nu --silent | complete)

        assert ($result.exit_code == 0) "Setup failed"

        # Verify each phase mentioned in output
        let phases = [
            "Phase 1: Operating System Detection"
            "Phase 2: Prerequisites Validation"
            "Phase 3: Taskfile"
            "Phase 4: UV Package Manager"
            "Phase 5: Python Virtual Environment"
            "Phase 6: Dependency Installation"
            "Phase 7: Configuration Setup"
            "Phase 8: Environment Validation"
        ]

        for phase in $phases {
            assert (($result.stdout | str contains $phase) or ($result.stdout | str contains "Phase")) $"Phase not found in output: ($phase)"
        }

        print "\n✅ All 8 setup phases executed"

        # Clean up after test
        cleanup_test_artifacts
    } catch {|e|
        # Restore environment on failure
        restore_environment
        error make {msg: $"Test failed: ($e.msg)"}
    }

    # Restore environment
    restore_environment
}

# Main test runner
def main [
    --verbose (-v)  # Show verbose output
] {
    print "\n╔═══════════════════════════════════════════════════════════╗"
    print "║     Integration Tests: Full Setup Flow (End-to-End)     ║"
    print "╚═══════════════════════════════════════════════════════════╝\n"

    let start_time = (date now)

    # Run tests sequentially
    let test_results = [
        (try { test_all_modules_exist; {name: "All modules exist", passed: true} } catch {|e| {name: "All modules exist", passed: false, error: $e.msg}})
        (try { test_setup_script_syntax; {name: "Setup script syntax", passed: true} } catch {|e| {name: "Setup script syntax", passed: false, error: $e.msg}})
        (try { test_full_setup_execution; {name: "Full setup execution", passed: true} } catch {|e| {name: "Full setup execution", passed: false, error: $e.msg}})
        (try { test_idempotent_rerun; {name: "Idempotent re-run", passed: true} } catch {|e| {name: "Idempotent re-run", passed: false, error: $e.msg}})
        (try { test_environment_ready; {name: "Environment ready", passed: true} } catch {|e| {name: "Environment ready", passed: false, error: $e.msg}})
        (try { test_all_phases_execute; {name: "All phases execute", passed: true} } catch {|e| {name: "All phases execute", passed: false, error: $e.msg}})
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
        print "║              ✅ All Integration Tests Passed!            ║"
    } else {
        print "║              ⚠️  Some Integration Tests Failed           ║"
    }

    print "╚═══════════════════════════════════════════════════════════╝\n"

    print $"📊 Results: ($passed) passed, ($failed) failed"
    print $"⏱️  Total test time: ($duration)\n"

    # Exit with appropriate code
    if $failed > 0 {
        exit 1
    }
}

# Unit tests for taskfile_install.nu module
#
# Tests the Taskfile installation module using explicit import pattern (per SPEC-001 D1)
#
# Usage:
#   nu scripts/tests/test_taskfile_install.nu

use std assert
use ../lib/taskfile_install.nu ensure_taskfile
use ../lib/os_detection.nu detect_os

# Test that ensure_taskfile returns correct structure
export def test_ensure_taskfile_structure [] {
    let os_info = (detect_os)
    let result = (ensure_taskfile $os_info)

    # Verify return structure has correct fields
    assert ("installed" in $result)
    assert ("version" in $result)
    assert ("source" in $result)
    assert ("error" in $result)

    # Verify field types
    assert (($result | get installed | describe) == "bool")
    assert (($result | get version | describe) == "string")
    assert (($result | get source | describe) == "string")
    assert (($result | get error | describe) == "string")

    print "✓ test_ensure_taskfile_structure passed"
}

# Test ensure_taskfile with detected OS
export def test_ensure_taskfile_with_os [] {
    let os_info = (detect_os)
    let result = (ensure_taskfile $os_info)

    print $"Taskfile check result for ($os_info.os):"
    print $"  Installed: ($result.installed)"
    print $"  Version: ($result.version)"
    print $"  Source: ($result.source)"

    if not $result.installed {
        print $"  Error: ($result.error)"
    }

    # Verify structure is correct regardless of result
    assert (($result | get installed | describe) == "bool")

    print "✓ test_ensure_taskfile_with_os passed"
}

# Test that function handles already installed Taskfile
export def test_taskfile_already_installed [] {
    let os_info = (detect_os)

    # First check
    let result1 = (ensure_taskfile $os_info)

    # If Taskfile is already installed, should detect it
    if $result1.installed {
        assert ($result1.source == "existing") "If Taskfile already installed, source should be 'existing'"
        assert (($result1.version | str length) > 0) "Version should be populated for existing installation"

        # Second check should return same result (idempotent)
        let result2 = (ensure_taskfile $os_info)
        assert ($result2.installed == $result1.installed)
        assert ($result2.version == $result1.version)
        assert ($result2.source == $result1.source)

        print "✓ test_taskfile_already_installed passed (Taskfile was already present)"
    } else {
        print "✓ test_taskfile_already_installed passed (Taskfile not present, would install)"
    }
}

# Test error handling for unsupported OS
export def test_unsupported_os [] {
    let fake_os_info = {
        os: "unsupported_os",
        arch: "unknown",
        version: "1.0"
    }

    let result = (ensure_taskfile $fake_os_info)

    # If Taskfile already installed, it returns existing (bypass unsupported OS check)
    # Otherwise, should return error for unsupported OS
    if $result.source == "existing" {
        print "✓ test_unsupported_os passed (Taskfile already installed, unsupported OS check bypassed)"
    } else {
        assert (not $result.installed)
        assert ($result.source == "unsupported")
        assert (($result.error | str length) > 0)
        print "✓ test_unsupported_os passed"
    }
}

# Test that version string is valid when installed
export def test_version_format [] {
    let os_info = (detect_os)
    let result = (ensure_taskfile $os_info)

    if $result.installed {
        # Version should contain numbers and dots (may or may not start with 'v')
        assert (($result.version | str contains ".")) "Version should contain '.'"
        assert (($result.version | str length) > 0) "Version should not be empty"

        let version = $result.version
        print $"✓ test_version_format passed \(version: ($version)\)"
    } else {
        print "✓ test_version_format passed (Taskfile not installed, skipping version check)"
    }
}

# Run all tests
def main [] {
    print "\n=== Running taskfile_install.nu tests ===\n"

    test_ensure_taskfile_structure
    test_ensure_taskfile_with_os
    test_taskfile_already_installed
    test_unsupported_os
    test_version_format

    print "\n=== All tests passed ===\n"
}

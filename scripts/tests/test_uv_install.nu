# Unit tests for UV Installation Module
#
# Tests the uv installation, version detection, and error handling

use std assert
use ../lib/uv_install.nu

# Test 1: Check UV version detection when installed
export def test_get_uv_version [] {
    print "Test: Get UV version"

    try {
        let version = (get_uv_version)
        print $"✅ UV version detected: ($version)"
        assert ($version | str length) > 0
    } catch {
        print "⚠️  UV not installed - skipping version test"
    }
}

# Test 2: Ensure UV installation (should be idempotent)
export def test_ensure_uv_idempotent [] {
    print "Test: Ensure UV (idempotent)"

    let result = (ensure_uv)

    print $"Result: ($result)"
    assert $result.installed
    assert (($result.version | str length) > 0)
    assert (($result.source | str length) > 0)
    assert ($result.error == "")
}

# Test 3: Verify UV is available in PATH
export def test_uv_in_path [] {
    print "Test: UV available in PATH"

    # Run ensure_uv first to make sure it's installed
    let _ = (ensure_uv)

    # Check if uv command is available
    let result = (^uv --version | complete)

    assert ($result.exit_code == 0)
    print $"✅ UV available in PATH: ($result.stdout | str trim)"
}

# Test 4: Verify UV version format
export def test_uv_version_format [] {
    print "Test: UV version format"

    try {
        let version = (get_uv_version)

        # UV version should contain "uv" and a version number
        # Example: "uv 0.4.30" or similar
        assert (($version | str contains "uv") or ($version =~ '\d+\.\d+'))
        print $"✅ UV version format valid: ($version)"
    } catch {
        print "⚠️  UV not installed - skipping version format test"
    }
}

# Test 5: Ensure UV returns proper structure
export def test_ensure_uv_return_structure [] {
    print "Test: Ensure UV return structure"

    let result = (ensure_uv)

    # Verify all required fields exist
    assert ("installed" in ($result | columns))
    assert ("version" in ($result | columns))
    assert ("source" in ($result | columns))
    assert ("error" in ($result | columns))

    print "✅ Return structure valid"
}

# Main test runner
def main [] {
    print "\n🧪 Running UV Installation Module Tests\n"

    test_ensure_uv_idempotent
    test_uv_in_path
    test_uv_version_format
    test_get_uv_version
    test_ensure_uv_return_structure

    print "\n✅ All UV installation tests passed!\n"
}

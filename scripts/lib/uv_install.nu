# UV Package Manager Validation Module
#
# This module checks if UV package manager is installed and available in the devbox environment.
# Installation should be handled via devbox.json, not by this script.
#
# Public Functions:
# - check_uv_installed: Check if UV is installed and get version

use common.nu *

# Check if uv is already installed
# Returns: record {installed: bool, version: string, error: string}
export def check_uv_installed [] {
    print "🔍 Checking for uv package manager..."

    # Check if uv binary exists
    let binary_check = (check_binary_exists "uv")

    if not $binary_check.exists {
        return {
            installed: false,
            version: "",
            error: "UV package manager not found in PATH. Please add 'uv' to devbox.json"
        }
    }

    # Get version
    let version_result = (get_binary_version "uv" "--version")

    if $version_result.success {
        print $"✅ UV installed: ($version_result.version)"
        return {
            installed: true,
            version: $version_result.version,
            error: ""
        }
    } else {
        return {
            installed: false,
            version: "",
            error: $"UV found but version check failed: ($version_result.error)"
        }
    }
}

# Get installed uv version (convenience function)
# Returns: string (version) or error
export def get_uv_version [] {
    let version_result = (get_binary_version "uv" "--version")

    if $version_result.success {
       return $version_result.version
    } else {
        error make {msg: "UV is not installed"}
    }
}

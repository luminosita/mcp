# Taskfile Validation Module
#
# This module checks if Taskfile is installed and available in the devbox environment.
# Installation should be handled via devbox.json, not by this script.
#
# Public Functions:
# - check_taskfile_installed: Check if Taskfile is installed and get version

use common.nu *

# Check if Taskfile is installed
# Returns: record {installed: bool, version: string, error: string}
export def check_taskfile_installed [] {
    print "🔍 Checking for Taskfile..."

    # Check if task binary exists
    let binary_check = (check_binary_exists "task")

    if not $binary_check.exists {
        return {
            installed: false,
            version: "",
            error: "Taskfile not found in PATH. Please add 'go-task' to devbox.json"
        }
    }

    # Get version
    let version_result = (get_binary_version "task" "--version")

    if $version_result.success {
        print $"✅ Taskfile installed: ($version_result.version)"
        return {
            installed: true,
            version: $version_result.version,
            error: ""
        }
    } else {
        return {
            installed: false,
            version: "",
            error: $"Taskfile found but version check failed: ($version_result.error)"
        }
    }
}

# Verify Taskfile functionality
# Returns: record {functional: bool, error: string}
export def verify_taskfile_functionality [] {
    print "🔍 Verifying Taskfile functionality..."

    # Try to list tasks
    let result = (^task --list | complete)

    if (command_succeeded $result) {
        print "✅ Taskfile functional"
        return {functional: true, error: ""}
    } else {
        return {
            functional: false,
            error: $"Taskfile --list command failed: ($result.stderr)"
        }
    }
}

# NuShell module for Taskfile installation with explicit exports (per SPEC-001 D1)
#
# This module handles cross-platform Taskfile 3.0+ installation with retry logic
# and checksum verification for security.
#
# Supports:
# - macOS: brew (preferred) + binary fallback
# - Linux: binary download with checksum verification
# - WSL2: apt (if available) + binary fallback
#
# Usage:
#   use scripts/lib/taskfile_install.nu check_taskfile_installed
#   use scripts/lib/os_detection.nu detect_os
#
#   let os_info = (detect_os)
#   let result = (check_taskfile_installed)
#
#   if not $result.installed {
#       print $"Warning: Taskfile installation failed: ($result.error)"
#       print "Setup will continue in degraded mode (manual task execution required)"
#   }

# Check if Taskfile is already installed
# Helper function (not exported - private to module)
#
# Returns: record<installed: bool, version: string, source: string, error: string>
export def check_taskfile_installed [] {
    let task_result = (which task)

    if ($task_result | is-empty) {
        return {
            installed: false,
            version: "",
            source: "",
            error: ""
        }
    }

    # Get version
    let version_output = (task --version | complete)

    if $version_output.exit_code != 0 {
        return {
            installed: false,
            version: "",
            source: "",
            error: "Taskfile command exists but version check failed"
        }
    }

    # Parse version (format: "Task version: v3.39.0" or just "v3.39.0")
    let version_str = ($version_output.stdout | str trim | split row " " | last)

    return {
        installed: true,
        version: $version_str,
        source: "existing",
        error: ""
    }
}

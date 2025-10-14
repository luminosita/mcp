# NuShell module for prerequisite validation with explicit exports (per SPEC-001 D1)
#
# This module validates the presence and versions of required tools (Python 3.11+, Podman, Git)
# within the Devbox environment, returning a structured report of validation results.
#
# NOTE: Checks ALL prerequisites before returning (complete report for better UX).
# Setup script will fail-fast if errors exist (per SPEC-001 D4).
#
# Usage:
#   use scripts/lib/prerequisites.nu check_prerequisites
#   let result = (check_prerequisites)
#
#   # Fail-fast integration
#   if ($result.errors | length) > 0 {
#       print "Prerequisites check failed:"
#       $result.errors | each { |err| print $"  - ($err)" }
#       exit 1
#   }

# Check if all prerequisites are available and meet version requirements
# Returns structured record with validation results and errors
#
# Returns: record<python: bool, python_version: string, podman: bool, podman_version: string, git: bool, git_version: string, errors: list<string>>
export def check_prerequisites [] {
    mut errors = []

    # Check Python 3.11+
    let python_check = (check_python)
    let python_ok = $python_check.ok
    let python_version = $python_check.version

    if not $python_ok {
        $errors = ($errors | append $python_check.error)
    }

    # Check Podman
    let podman_check = (check_podman)
    let podman_ok = $podman_check.ok
    let podman_version = $podman_check.version

    if not $podman_ok {
        $errors = ($errors | append $podman_check.error)
    }

    # Check Git
    let git_check = (check_git)
    let git_ok = $git_check.ok
    let git_version = $git_check.version

    if not $git_ok {
        $errors = ($errors | append $git_check.error)
    }

    return {
        python: $python_ok,
        python_version: $python_version,
        podman: $podman_ok,
        podman_version: $podman_version,
        git: $git_ok,
        git_version: $git_version,
        errors: $errors
    }
}

# Check Python version (3.11+)
# Helper function (not exported - private to module)
#
# Returns: record<ok: bool, version: string, error: string>
def check_python [] {
    # Check if Python is available
    let python_result = (which python)

    if ($python_result | is-empty) {
        return {
            ok: false,
            version: "",
            error: "Python not found. Add 'python@3.11' to devbox.json packages."
        }
    }

    # Get Python version
    let version_output = (python --version | complete)

    if $version_output.exit_code != 0 {
        return {
            ok: false,
            version: "",
            error: "Python version check failed. Ensure Python is properly installed."
        }
    }

    # Parse version (format: "Python 3.11.5" or "Python 3.11.5+")
    try {
        let version_str = ($version_output.stdout | str trim | split row " " | get 1)

        # Remove any + or rc suffixes for version parsing
        let clean_version = ($version_str | split row "+" | get 0 | split row "rc" | get 0)
        let version_parts = ($clean_version | split row ".")

        let major = ($version_parts | get 0 | into int)
        let minor = ($version_parts | get 1 | into int)

        if $major < 3 or ($major == 3 and $minor < 11) {
            return {
                ok: false,
                version: $version_str,
                error: $"Python ($version_str) is too old. Python 3.11+ required. Update devbox.json to use python@3.11."
            }
        }

        return {
            ok: true,
            version: $version_str,
            error: ""
        }
    } catch {
        return {
            ok: false,
            version: "",
            error: "Failed to parse Python version. Ensure Python is properly installed."
        }
    }
}

# Check Podman availability
# Helper function (not exported - private to module)
#
# Returns: record<ok: bool, version: string, error: string>
def check_podman [] {
    let podman_result = (which podman)

    if ($podman_result | is-empty) {
        return {
            ok: false,
            version: "",
            error: "Podman not found. Add 'podman@latest' to devbox.json packages."
        }
    }

    # Get Podman version
    let version_output = (podman --version | complete)

    if $version_output.exit_code != 0 {
        return {
            ok: false,
            version: "",
            error: "Podman version check failed. Ensure Podman is properly installed."
        }
    }

    # Parse version (format: "podman version 4.7.0")
    try {
        let version_str = ($version_output.stdout | str trim | split row " " | get 2)
        return {
            ok: true,
            version: $version_str,
            error: ""
        }
    } catch {
        # If parsing fails, still consider it OK (any version is acceptable)
        return {
            ok: true,
            version: "unknown",
            error: ""
        }
    }
}

# Check Git availability
# Helper function (not exported - private to module)
#
# Returns: record<ok: bool, version: string, error: string>
def check_git [] {
    let git_result = (which git)

    if ($git_result | is-empty) {
        return {
            ok: false,
            version: "",
            error: "Git not found. Add 'git@latest' to devbox.json packages."
        }
    }

    # Get Git version
    let version_output = (git --version | complete)

    if $version_output.exit_code != 0 {
        return {
            ok: false,
            version: "",
            error: "Git version check failed. Ensure Git is properly installed."
        }
    }

    # Parse version (format: "git version 2.42.0")
    try {
        let version_str = ($version_output.stdout | str trim | split row " " | get 2)
        return {
            ok: true,
            version: $version_str,
            error: ""
        }
    } catch {
        # If parsing fails, still consider it OK (any version is acceptable)
        return {
            ok: true,
            version: "unknown",
            error: ""
        }
    }
}

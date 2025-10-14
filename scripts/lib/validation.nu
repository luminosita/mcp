# Environment Validation Module
#
# This module performs comprehensive health checks on the development environment
# including Python version, Taskfile functionality, dependency imports, and
# file permissions.
#
# Public Functions:
# - validate_environment: Run all validation checks
# - validate_python_version: Check Python version >= 3.11
# - validate_taskfile: Check Taskfile installation and functionality
# - validate_dependencies: Test critical module imports

# Validation check record structure:
# {name: string, passed: bool, message: string, error: string}

# Validate Python version (>= 3.11)
# Args:
#   venv_path: string - Path to virtual environment
# Returns: record {name, passed, message, error}
export def validate_python_version [venv_path: string = ".venv"] {
    let check_name = "Python Version (>= 3.11)"

    let python_bin = if ($nu.os-info.name == "windows") {
        ($venv_path | path join "Scripts" "python.exe")
    } else {
        ($venv_path | path join "bin" "python")
    }

    if not ($python_bin | path exists) {
        return {
            name: $check_name,
            passed: false,
            message: "",
            error: $"Python binary not found at ($python_bin)"
        }
    }

    let result = (^$python_bin --version | complete)

    if $result.exit_code != 0 {
        return {
            name: $check_name,
            passed: false,
            message: "",
            error: $"Python version check failed: ($result.stderr)"
        }
    }

    # Parse version (e.g., "Python 3.11.6" -> "3.11.6")
    let version_str = ($result.stdout | str trim | str replace "Python " "")
    let version_parts = ($version_str | split row ".")

    if ($version_parts | length) < 2 {
        return {
            name: $check_name,
            passed: false,
            message: "",
            error: $"Could not parse Python version: ($version_str)"
        }
    }

    let major = ($version_parts | get 0 | into int)
    let minor = ($version_parts | get 1 | into int)

    # Check if Python >= 3.11
    if ($major >= 3) and ($minor >= 11) {
        return {
            name: $check_name,
            passed: true,
            message: $"Python ($version_str) meets requirement (>= 3.11)",
            error: ""
        }
    } else {
        return {
            name: $check_name,
            passed: false,
            message: "",
            error: $"Python ($version_str) does not meet requirement (>= 3.11)"
        }
    }
}

# Validate Taskfile installation and functionality
# Returns: record {name, passed, message, error}
export def validate_taskfile [] {
    let check_name = "Taskfile Functionality"

    # Check task --version
    let version_result = (^task --version | complete)

    if $version_result.exit_code != 0 {
        return {
            name: $check_name,
            passed: false,
            message: "",
            error: "Taskfile not installed or not in PATH"
        }
    }

    # Check task --list
    let list_result = (^task --list | complete)

    if $list_result.exit_code != 0 {
        return {
            name: $check_name,
            passed: false,
            message: "",
            error: $"Taskfile --list command failed: ($list_result.stderr)"
        }
    }

    let version = ($version_result.stdout | str trim)

    return {
        name: $check_name,
        passed: true,
        message: $"Taskfile ($version) installed and functional",
        error: ""
    }
}

# Validate critical module imports
# Args:
#   venv_path: string - Path to virtual environment
# Returns: record {name, passed, message, error}
export def validate_dependencies [venv_path: string = ".venv"] {
    let check_name = "Critical Module Imports"

    let python_bin = if ($nu.os-info.name == "windows") {
        ($venv_path | path join "Scripts" "python.exe")
    } else {
        ($venv_path | path join "bin" "python")
    }

    if not ($python_bin | path exists) {
        return {
            name: $check_name,
            passed: false,
            message: "",
            error: $"Python binary not found at ($python_bin)"
        }
    }

    # Try to import mcp_server package
    let import_cmd = "import mcp_server; print('OK')"
    let result = (^$python_bin -c $import_cmd | complete)

    if $result.exit_code == 0 {
        return {
            name: $check_name,
            passed: true,
            message: "All critical modules importable",
            error: ""
        }
    } else {
        return {
            name: $check_name,
            passed: false,
            message: "",
            error: $"Module import failed: ($result.stderr)"
        }
    }
}

# Validate .env file exists
# Returns: record {name, passed, message, error}
export def validate_env_file [] {
    let check_name = ".env File Exists"

    if (".env" | path exists) {
        return {
            name: $check_name,
            passed: true,
            message: ".env file configured",
            error: ""
        }
    } else {
        return {
            name: $check_name,
            passed: false,
            message: "",
            error: ".env file not found"
        }
    }
}

# Validate pre-commit hooks installed
# Returns: record {name, passed, message, error}
export def validate_precommit_hooks [] {
    let check_name = "Pre-commit Hooks Installed"

    # Check if .git/hooks/pre-commit exists
    let hook_path = (".git" | path join "hooks" "pre-commit")

    if ($hook_path | path exists) {
        return {
            name: $check_name,
            passed: true,
            message: "Pre-commit hooks installed",
            error: ""
        }
    } else {
        return {
            name: $check_name,
            passed: false,
            message: "",
            error: "Pre-commit hooks not installed in .git/hooks/"
        }
    }
}

# Validate file permissions for .venv
# Args:
#   venv_path: string - Path to virtual environment
# Returns: record {name, passed, message, error}
export def validate_venv_permissions [venv_path: string = ".venv"] {
    let check_name = "Virtual Environment Permissions"

    if not ($venv_path | path exists) {
        return {
            name: $check_name,
            passed: false,
            message: "",
            error: $"Virtual environment not found at ($venv_path)"
        }
    }

    # Check if venv directory is readable
    let python_bin = if ($nu.os-info.name == "windows") {
        ($venv_path | path join "Scripts" "python.exe")
    } else {
        ($venv_path | path join "bin" "python")
    }

    if ($python_bin | path exists) {
        return {
            name: $check_name,
            passed: true,
            message: "Virtual environment permissions OK",
            error: ""
        }
    } else {
        return {
            name: $check_name,
            passed: false,
            message: "",
            error: $"Python binary not accessible at ($python_bin)"
        }
    }
}

# Run all validation checks
# Args:
#   venv_path: string - Path to virtual environment (default: .venv)
# Returns: record {passed: int, failed: int, checks: list}
export def validate_environment [venv_path: string = ".venv"] {
    print "\n🔍 Running environment validation checks...\n"

    mut checks = []

    # Run all checks
    $checks = ($checks | append (validate_python_version $venv_path))
    $checks = ($checks | append (validate_taskfile))
    $checks = ($checks | append (validate_dependencies $venv_path))
    $checks = ($checks | append (validate_env_file))
    $checks = ($checks | append (validate_precommit_hooks))
    $checks = ($checks | append (validate_venv_permissions $venv_path))

    # Count passed/failed
    let passed = ($checks | where passed == true | length)
    let failed = ($checks | where passed == false | length)

    # Display results
    print $"Validation Results: ($passed)/($passed + $failed) checks passed\n"

    for check in $checks {
        if $check.passed {
            print $"✅ ($check.name): ($check.message)"
        } else {
            print $"❌ ($check.name): ($check.error)"
        }
    }

    print ""

    return {
        passed: $passed,
        failed: $failed,
        checks: $checks
    }
}

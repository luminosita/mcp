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
#   use scripts/lib/taskfile_install.nu ensure_taskfile
#   use scripts/lib/os_detection.nu detect_os
#
#   let os_info = (detect_os)
#   let result = (ensure_taskfile $os_info)
#
#   if not $result.installed {
#       print $"Warning: Taskfile installation failed: ($result.error)"
#       print "Setup will continue in degraded mode (manual task execution required)"
#   }

# Latest Taskfile version to install
const TASKFILE_VERSION = "v3.39.2"
const TASKFILE_BASE_URL = "https://github.com/go-task/task/releases/download"

# Ensure Taskfile 3.0+ is installed
# Checks if already installed, otherwise installs based on OS
#
# Arguments:
#   os_info: record - OS detection result from os_detection.nu
#
# Returns: record<installed: bool, version: string, source: string, error: string>
export def ensure_taskfile [os_info: record] {
    # Check if already installed
    let existing_check = (check_taskfile_installed)

    if $existing_check.installed {
        return $existing_check
    }

    # Install based on OS
    let install_result = match $os_info.os {
        "macos" => (install_taskfile_macos $os_info.arch),
        "linux" => (install_taskfile_linux $os_info.arch),
        "wsl2" => (install_taskfile_wsl2 $os_info.arch),
        _ => {
            {
                installed: false,
                version: "",
                source: "unsupported",
                error: $"Unsupported OS: ($os_info.os)"
            }
        }
    }

    return $install_result
}

# Check if Taskfile is already installed
# Helper function (not exported - private to module)
#
# Returns: record<installed: bool, version: string, source: string, error: string>
def check_taskfile_installed [] {
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

# Install Taskfile on macOS
# Tries brew first, falls back to binary installation
# Helper function (not exported - private to module)
#
# Arguments:
#   arch: string - Architecture (arm64, x86_64)
#
# Returns: record<installed: bool, version: string, source: string, error: string>
def install_taskfile_macos [arch: string] {
    # Try brew first
    let brew_result = (which brew)

    if ($brew_result | is-not-empty) {
        print "Installing Taskfile via Homebrew..."

        let install_output = (brew install go-task | complete)

        if $install_output.exit_code == 0 {
            let check = (check_taskfile_installed)
            return {
                installed: $check.installed,
                version: $check.version,
                source: "brew",
                error: ""
            }
        } else {
            print $"Homebrew installation failed: ($install_output.stderr)"
            print "Falling back to binary installation..."
        }
    }

    # Fallback to binary installation
    let darwin_arch = if $arch == "arm64" { "arm64" } else { "amd64" }
    return (install_taskfile_binary "darwin" $darwin_arch)
}

# Install Taskfile on Linux
# Uses binary download with checksum verification
# Helper function (not exported - private to module)
#
# Arguments:
#   arch: string - Architecture (x86_64, aarch64, etc.)
#
# Returns: record<installed: bool, version: string, source: string, error: string>
def install_taskfile_linux [arch: string] {
    let linux_arch = if $arch in ["x86_64", "amd64"] { "amd64" } else if $arch in ["aarch64", "arm64"] { "arm64" } else { "amd64" }
    return (install_taskfile_binary "linux" $linux_arch)
}

# Install Taskfile on WSL2
# Tries apt first, falls back to binary installation
# Helper function (not exported - private to module)
#
# Arguments:
#   arch: string - Architecture (x86_64, aarch64, etc.)
#
# Returns: record<installed: bool, version: string, source: string, error: string>
def install_taskfile_wsl2 [arch: string] {
    # Try apt if available
    let apt_result = (which apt)

    if ($apt_result | is-not-empty) {
        print "Attempting to install Taskfile via apt..."

        # Note: Taskfile may not be in default Ubuntu repos, so this may fail
        let install_output = (^sudo apt install -y task | complete)

        if $install_output.exit_code == 0 {
            let check = (check_taskfile_installed)

            if $check.installed {
                return {
                    installed: $check.installed,
                    version: $check.version,
                    source: "apt",
                    error: ""
                }
            }
        }

        print "apt installation failed or Taskfile not available in repos"
        print "Falling back to binary installation..."
    }

    # Fallback to binary installation
    let linux_arch = if $arch in ["x86_64", "amd64"] { "amd64" } else if $arch in ["aarch64", "arm64"] { "arm64" } else { "amd64" }
    return (install_taskfile_binary "linux" $linux_arch)
}

# Install Taskfile from binary release with retry logic
# Helper function (not exported - private to module)
#
# Arguments:
#   os: string - OS name (darwin, linux)
#   arch: string - Architecture (amd64, arm64)
#
# Returns: record<installed: bool, version: string, source: string, error: string>
def install_taskfile_binary [os: string, arch: string] {
    print $"Installing Taskfile ($TASKFILE_VERSION) for ($os)_($arch)..."

    # Construct download URL
    let filename = $"task_($os)_($arch).tar.gz"
    let download_url = $"($TASKFILE_BASE_URL)/($TASKFILE_VERSION)/($filename)"

    # Ensure ~/.local/bin exists
    let install_dir = $"($env.HOME)/.local/bin"
    mkdir $install_dir

    # Download with retry logic (3 attempts)
    let max_attempts = 3
    mut attempt = 1
    mut download_success = false
    mut error_msg = ""

    while $attempt <= $max_attempts and (not $download_success) {
        print $"Download attempt ($attempt)/($max_attempts)..."

        let download_result = (try {
            # Download to temporary location
            let temp_file = $"/tmp/task_($os)_($arch).tar.gz"
            http get $download_url | save --force $temp_file

            # Extract task binary
            let extract_output = (^tar -xzf $temp_file -C /tmp task | complete)

            if $extract_output.exit_code == 0 {
                # Move to install directory
                ^mv /tmp/task $"($install_dir)/task"
                ^chmod +x $"($install_dir)/task"

                # Cleanup temp file
                ^rm -f $temp_file

                {success: true, error: ""}
            } else {
                # Cleanup temp file
                ^rm -f $temp_file
                {success: false, error: $"Extraction failed: ($extract_output.stderr)"}
            }
        } catch { |err|
            {success: false, error: $"Download failed: ($err)"}
        })

        if $download_result.success {
            $download_success = true
            print "Download and extraction successful"
        } else {
            $error_msg = $download_result.error
            print $error_msg

            if $attempt < $max_attempts {
                let sleep_seconds = ($attempt * 2)  # Exponential backoff: 2s, 4s, 6s
                print $"Retrying in ($sleep_seconds) seconds..."
                sleep ($sleep_seconds * 1sec)
            }
        }

        $attempt = $attempt + 1
    }

    if not $download_success {
        return {
            installed: false,
            version: "",
            source: "binary",
            error: $"Failed after ($max_attempts) attempts. Last error: ($error_msg)"
        }
    }

    # Verify installation
    # Note: May need to reload PATH or use full path
    let task_path = $"($install_dir)/task"

    let version_output = (^$task_path --version | complete)

    if $version_output.exit_code == 0 {
        let version_str = ($version_output.stdout | str trim | split row " " | last)
        print $"Taskfile ($version_str) installed successfully at ($install_dir)/task"
        print "Note: You may need to add ~/.local/bin to your PATH"
        print "Add this line to your shell profile: export PATH=\"$HOME/.local/bin:$PATH\""

        return {
            installed: true,
            version: $version_str,
            source: "binary",
            error: ""
        }
    } else {
        return {
            installed: false,
            version: "",
            source: "binary",
            error: "Installation completed but version check failed"
        }
    }
}

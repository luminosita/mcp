# UV Package Manager Installation Module
#
# This module handles the installation of uv package manager across different platforms.
# It checks if uv is already installed, downloads and installs it if needed, and verifies
# the installation.
#
# Public Functions:
# - ensure_uv: Main function to ensure uv is installed
# - get_uv_version: Get installed uv version

# Check if uv is already installed
# Returns: record {installed: bool, version: string}
def check_uv_installed [] {
    let result = (^uv --version | complete)

    if $result.exit_code == 0 {
        let version = ($result.stdout | str trim)
        return {installed: true, version: $version}
    } else {
        return {installed: false, version: ""}
    }
}

# Install uv using the official installer
# Returns: record {success: bool, error: string}
def install_uv_via_installer [] {
    print "📦 Downloading uv installer..."

    # Use the official uv installation script
    let install_result = (
        ^curl -LsSf https://astral.sh/uv/install.sh | ^sh
        | complete
    )

    if $install_result.exit_code == 0 {
        print "✅ UV installer completed successfully"

        # Update PATH for current session
        # UV installs to ~/.cargo/bin by default
        let cargo_bin = ($env.HOME | path join ".cargo" "bin")

        # Check if uv binary exists
        if ($cargo_bin | path join "uv" | path exists) {
            # Add to PATH if not already there
            if not ($env.PATH | any {|p| $p == $cargo_bin}) {
                $env.PATH = ($env.PATH | append $cargo_bin)
            }
            return {success: true, error: ""}
        } else {
            return {
                success: false,
                error: $"UV binary not found at ($cargo_bin)/uv after installation"
            }
        }
    } else {
        return {
            success: false,
            error: $"UV installation failed: ($install_result.stderr)"
        }
    }
}

# Retry UV installation with exponential backoff
# Returns: record {success: bool, error: string, attempts: int}
def install_with_retry [] {
    let max_attempts = 3
    let backoff = [1sec 2sec 4sec]

    for attempt in 0..<$max_attempts {
        print $"Attempt ($attempt + 1) of ($max_attempts)..."

        let result = (install_uv_via_installer)

        if $result.success {
            return {success: true, error: "", attempts: ($attempt + 1)}
        }

        # If not last attempt, wait before retrying
        if $attempt < ($max_attempts - 1) {
            let wait_time = ($backoff | get $attempt)
            print $"⏳ Waiting ($wait_time) before retry..."
            sleep $wait_time
        }
    }

    return {
        success: false,
        error: "UV installation failed after 3 attempts",
        attempts: $max_attempts
    }
}

# Main function: Ensure uv is installed
# Returns: record {installed: bool, version: string, source: string, error: string}
export def ensure_uv [] {
    print "🔍 Checking for uv package manager..."

    # Check if already installed
    let check = (check_uv_installed)

    if $check.installed {
        print $"✅ UV already installed: ($check.version)"
        return {
            installed: true,
            version: $check.version,
            source: "existing",
            error: ""
        }
    }

    # Install uv
    print "📥 Installing uv package manager..."
    let install = (install_with_retry)

    if not $install.success {
        return {
            installed: false,
            version: "",
            source: "",
            error: $install.error
        }
    }

    # Verify installation
    let verify = (check_uv_installed)

    if $verify.installed {
        print $"✅ UV installed successfully: ($verify.version)"
        let source_desc = $"downloaded \(($install.attempts) attempts)"
        return {
            installed: true,
            version: $verify.version,
            source: $source_desc,
            error: ""
        }
    } else {
        return {
            installed: false,
            version: "",
            source: "",
            error: "UV installation verification failed - command not found after install"
        }
    }
}

# Get installed uv version
# Returns: string (version) or error
export def get_uv_version [] {
    let check = (check_uv_installed)

    if $check.installed {
        return $check.version
    } else {
        error make {msg: "UV is not installed"}
    }
}

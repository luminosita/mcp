# UV Package Manager Installation Module
#
# This module handles the installation of uv package manager across different platforms.
# It checks if uv is already installed, downloads and installs it if needed, and verifies
# the installation.
#
# Public Functions:
# - check_uv_installed: Main function to check if uv is installed
# - get_uv_version: Get installed uv version

# Check if uv is already installed
# Returns: record {installed: bool, version: string}
export def check_uv_installed [] {
    let result = (^uv --version | complete)

    if $result.exit_code == 0 {
        let version = ($result.stdout | str trim)
        return {installed: true, version: $version}
    } else {
        return {installed: false, version: ""}
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

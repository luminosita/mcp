## Installation of Binaries Removed

### Ensure methods

- export def ensure_taskfile [os_info: record]
- export def ensure_uv []

**Rationale**: We are using devbox isolated environment. Implementation must happen within the environment. Missing binaries/libraries must be corrected by updating `devbox.json` instead of installation via package managers

## Code duplication within scripts/lib

### Examples

- Python binary with path (and variations)

```shell
    let python_bin = if ($nu.os-info.name == "windows") {
        ($venv_path | path join "Scripts" "python.exe")
    } else {
        ($venv_path | path join "bin" "python")
    }

    if not ($python_bin | path exists) {
```

- Taskfile exists (and variations)

```shell
    let version_result = (^task --version | complete)

    if $version_result.exit_code != 0 {
        return {
            name: $check_name,
            passed: false,
            message: "",
            error: "Taskfile not installed or not in PATH"
        }
    }
```

- Version verification

`get_uv_version` in `uv_install.nu` has the same result as `check_uv_installed.version`
```shell
get_uv_version
```

### Proposed Fix

These type of patterns must be part of some common module, and be reused instead of recreated all the time


**ADDED Critique**

## venv_setup.nu

C1: What is the difference between `get_python_version` and `get_venv_python_version`? Can it be consolidated?

C2: `validation.nu` should not check if binaries exists. All methods in `setup.nu` already performed that validation

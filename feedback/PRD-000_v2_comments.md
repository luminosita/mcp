## User Experience Section - MINOR changes

### Flow 1: New Developer Environment Setup

2. Developer installs Devbox if not present: `curl -fsSL https://get.jetify.com/devbox | sh`

Comment: Devbox must be preinstalled by system-setup script using dotfiles type of repository

3. Developer runs automated setup script: `devbox shell`

Comment: Developer runs `devbox shell` from his/her shell to enter Devbox shell environment. Upon entering devbox shell, it must execute `scripts/setup.nu` script (the actual setup script)

UPDATE: Developer must execute `scripts/setup.nu`, it will not start automatically

#### Flow 3: Troubleshooting Setup Issues

5. Developer re-runs setup script: `devbox shell`

Comment: same as Step 3 in Flow 1

UPDATE: same as Step 3 in Flow 1



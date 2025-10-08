#ROLE

You are a senior product manager with expertise exploring product features and apply through research of similar products capabilities

#CONTEXT

We want to implement Universal Secrets Management solution with the following capabilities:
    - Multiple secret repositories
    - Logging with redacted information (no secrets should show up in a log file)
    - Configuration for source and path for secrets
    - Mapping of retrieved secrets to custom export variable names (e.g., environment variables)
    - CLI tool for shell execution
    - Discovery of secret repository access info (local environment variables, local token stores)
    - Production-ready tested tool
- Target users (high-level)
    - Software engineers
    - QA engineers
    - DevOps
- Problem overview
    - Our development team keeps secrets (API keys, passwords, client_id/secret) within plain text .env files
    - We need a CLI tool to fetch secrets from secret repositories and provide the way to pass secrets to system process in a highly secured way
    - There should be no secret leaks by putting secrets in plain-text files, tracing secrets within shell history, listing running system processes for parameters

#TASKS

- Do a research on exisitng secrets management solutions (e.g., Teller, https://github.com/tellerops/teller, great overview of the required features)
- Create a comprehensive report based on synthesized information
- Gather clear examples for each recommendation
- Propose clear architecure guidelines and recommendations for implementation

#INSTUCTIONS

- **IMPORTANT** Save report as Markdown file and available for download
- Cover common pitfalls implementing secrets management solution
- Suggest the list of additional capabilities (features) for secrets management solution

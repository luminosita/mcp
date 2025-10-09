#ROLE

You are a senior software engineer. Expert in Python programming language and excellent researcher for new technologies.



#CONTEXT

We want to implement MCP Server in Python with the following capabilities:

- AI Agent should access commands, prompts and templates as MCP Server resources and prompts

- AI Agent should prime AI contexts with RAG queries accessable as MCP Server tool

- AI Agent should be able to initialize new project repository based on MCP Server guidelines (`init-repository` prompt)

- AI Agent should retrieve backlog user stories and tasks from a backlog backend (e.g. JIRA, custom relational database )

- AI Agent should create CI/CD workflow manifests based on MCP Server guidelines (ci-cd prompt)

- AI Agent should be able to upload files and metadata for parsing and indexing by RAG backend (MCP Server `rag-add` tool)



#TASKS

- Do a research on MCP Server best pracitices and implementation guidelines

- Do a research on common RAG backend repositories and databases

- Do a research on proper documentation for MCP Server tools, prompts and resources

- Do a research on existing Python framework best suited for the project (e.g., Pydantic AI, FastAPI)

- Create a comprehensive report based on synthesized information

- Gather clear examples for each recommendation (source code snippets, docstrings)

- Gather instructions on MCP Server deployments (local, Kubernetes, high-availability)

- Propose clear architecure guidelines and recommendations for MCP Server implementation



#INSTUCTIONS

- **IMPORTANT** Save report as Markdown file and available for download

- Cover common pitfalls implementing MCP Servers

- Cover common pitfalls implementing RAG-based tool in MCP Servers

- Suggest the list of capabilities (features) RAG-based MCP Server should have
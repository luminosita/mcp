# MCP Server Implementation Report

**Author:** Gemini, Senior Software Engineer
**Date:** October 8, 2025
**Version:** 1.1

**Changelog v1.1:**
* Added research on the "Pydantic AI" pattern for structured LLM output.
* Recommended `instructor` as a key library for the AI Agent's client-side logic.
* Included new implementation examples and architectural considerations for robust agent-to-server communication.

## 1. Executive Summary

This report outlines the research, architecture, and implementation plan for creating a **Multi-purpose Command and Prompting (MCP) Server** in Python. The MCP Server will act as a centralized hub, providing AI agents with standardized tools, versioned prompts, and access to organizational resources like backlogs and code repositories.

The core of this proposal is a modular architecture built on **FastAPI**, leveraging a powerful **Retrieval-Augmented Generation (RAG)** backend for context-aware operations. We recommend **Weaviate** or **PostgreSQL with `pgvector`** for production RAG backends due to their scalability and feature sets, with **ChromaDB** for local development. This approach will enable our AI agents to perform complex, context-aware tasks such as project initialization, CI/CD pipeline generation, and backlog management, all governed by the MCP Server.

Crucially, this report now also recommends a specific pattern for the **AI Agent's client-side implementation**. The agent's logic should leverage structured output generation (via libraries like **`instructor`**) to ensure reliable, schema-compliant communication with the server's tools, drastically reducing errors and improving overall system robustness.

---

## 2. Introduction: The MCP Server Concept

The MCP Server is an API-driven service designed to be the "brain" and "toolbelt" for AI agents operating within our development ecosystem. It decouples the agent's core logic from the specifics of our internal tools and processes.

**Key Objectives:**

* **Standardization:** Provide a single source of truth for prompts, templates, and operational logic.
* **Tooling:** Expose complex operations (like RAG queries, file uploads, JIRA access) as simple, well-documented tools for the agent.
* **Governance:** Enforce development best practices (e.g., repository structure, CI/CD manifests) programmatically.
* **Extensibility:** Allow for the easy addition of new tools, resources, and data sources without modifying the agent's core code.



---

## 3. Proposed Architecture & Technology Stack

We propose a modular, service-oriented architecture. The core of the server is a FastAPI application, while the AI Agent client is empowered by a structured output library.


### 3.1. MCP Server Technology

* **API Framework:** **FastAPI**. It's chosen for its high performance, native `async` support, Pydantic-based data validation, and automatic generation of OpenAPI (Swagger) documentation. This self-documentation is critical, as it allows agents (and developers) to discover and understand how to use the available tools.
* **RAG Backend (Vector Database):**
    * **Local/Development:** **ChromaDB**. It's lightweight, runs in-process or as a standalone server, and is extremely fast to set up.
    * **Production/Staging:** **Weaviate** or **PostgreSQL with `pgvector`**.
        * **Weaviate** is a feature-rich, open-source vector database that offers hybrid search (keyword + vector) and excellent scalability.
        * **`pgvector`** is a great choice if your team already has strong PostgreSQL expertise, as it keeps the tech stack smaller.
* **Data Parsing/Handling:** **Pydantic** for modeling all API requests and responses. Libraries like `LangChain` or `LlamaIndex` can be used to handle the document chunking, embedding, and indexing pipeline for the RAG backend.
* **Deployment:** **Docker** for containerization and **Kubernetes** for orchestration.
### 3.2. AI Agent Client-Side Technology (New Recommendation)

* **Structured Output Generation:** **`instructor`**. This library patches the OpenAI client to force LLM outputs into a specified Pydantic model. This is not part of the server, but is the recommended way for the agent to interact with the server.
* **Why `instructor`?** It solves the problem of LLM unreliability. Instead of prompting an LLM to "generate JSON in the right format," this pattern guarantees the output conforms to the Pydantic model required by the server's API, including validation and automated retries on failure.

---

## 4. Implementation Guidelines & Examples

Here we detail the implementation of core MCP Server features with code examples.

### 4.1. Framework: FastAPI

FastAPI's design is perfect for this use case. Its dependency injection system and Pydantic models make the code clean and robust.

```python
# main.py
from fastapi import FastAPI, HTTPException, UploadFile, File
from typing import List
from pydantic import BaseModel, Field

# Initialize the FastAPI app
app = FastAPI(
    title="MCP Server",
    description="Multi-purpose Command and Prompting Server for AI Agents",
    version="1.0.0"
)

# Dummy service connectors (replace with actual client logic)
from services import rag_service, backlog_service, project_service

# --- Pydantic Models ---
class RAGQuery(BaseModel):
    query_text: str
    top_k: int = 5

class RAGResult(BaseModel):
    source: str
    content: str
    score: float

class BacklogTask(BaseModel):
    id: str = Field(..., description="The unique identifier for the task, e.g., 'PROJ-123'.")
    title: str
    description: str
    status: str
    assignee: str | None

# --- API Endpoints ---
@app.get("/")
def read_root():
    return {"message": "MCP Server is operational."}
```

### 4.2. Server: Documenting and Serving Resources (Prompts)

Resources like prompts should be versioned and accessible via the API. Storing them in a structured format (e.g., YAML or JSON files) in your repository is a good practice.

```python
# main.py (continued)
import yaml

def load_prompt(prompt_name: str) -> str:
    """Loads a prompt template from the filesystem."""
    try:
        with open(f"resources/prompts/{prompt_name}.yaml", "r") as f:
            data = yaml.safe_load(f)
            return data.get("template", "")
    except FileNotFoundError:
        return None

@app.get("/prompts/{prompt_name}", tags=["Resources"])
def get_prompt(prompt_name: str):
    """
    Retrieves a versioned prompt template by its name.
    
    This endpoint allows an AI agent to fetch standardized prompts
    for tasks like initializing a new repository or generating a CI/CD manifest.
    """
    prompt_template = load_prompt(prompt_name)
    if not prompt_template:
        raise HTTPException(status_code=404, detail=f"Prompt '{prompt_name}' not found.")
    return {"name": prompt_name, "template": prompt_template}
```

**Example Prompt File (`resources/prompts/init-repository.yaml`):**

```yaml
version: "1.1"
author: "DevOps Team"
description: "System prompt for initializing a new Python project repository."
template: |
  You are an expert software engineering assistant. Your task is to initialize a new Python project repository.
  
  Follow these guidelines strictly:
  1. Create a root directory named `{repo_name}`.
  2. Inside, create a `pyproject.toml` file with basic metadata (name, version 0.1.0, description).
  3. Create a `src/{repo_name}` directory with an empty `__init__.py`.
  4. Create a `README.md` file with the repo name as the main header.
  5. Initialize a Git repository and create an initial commit with the message "feat: initial project structure".
```

### 4.3. Server: Implementing Tools for the AI Agent

Tools are simply API endpoints that perform a specific action. The descriptions in the docstrings and Pydantic models are crucial, as they will appear in the OpenAPI spec that the agent consumes.

#### `rag-prime` Tool (RAG Query)

This tool allows the agent to prime its context with relevant information.

```python
# main.py (continued)
@app.post("/tools/rag-query", response_model=List[RAGResult], tags=["Tools"])
async def rag_query_tool(query: RAGQuery):
    """
    Performs a semantic search against the knowledge base (RAG backend)
    to retrieve relevant context for a given query. This tool is used to
    prime the AI's context before generating a response.
    """
    try:
        # The query object is a validated Pydantic instance
        results = await rag_service.search(query.query_text, top_k=query.top_k)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### `rag-add` Tool (File Ingestion)

This tool allows the agent to upload new information to the RAG knowledge base.

```python
# main.py (continued)
@app.post("/tools/rag-add", tags=["Tools"])
async def rag_add_tool(file: UploadFile = File(...)):
    """
    Uploads a file to the RAG backend for parsing and indexing.
    The file content will be chunked, embedded, and stored in the
    vector database, making it available for future RAG queries.
    Supported formats: .md, .txt, .pdf.
    """
    if not file.filename.endswith(('.md', '.txt', '.pdf')):
        raise HTTPException(status_code=400, detail="Invalid file type.")
    
    content = await file.read()
    try:
        # The rag_service.add method handles chunking, embedding, and indexing
        document_id = await rag_service.add(
            content=content, 
            metadata={"source": file.filename}
        )
        return {"message": "File processed successfully.", "document_id": document_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {e}")
```

#### `get-backlog` Tool

This tool retrieves tasks from a project management system like JIRA.

```python
# main.py (continued)
@app.get("/tools/get-backlog/{project_key}", response_model=List[BacklogTask], tags=["Tools"])
async def get_project_backlog_tool(project_key: str):
    """
    Retrieves a list of open user stories and tasks for a given project key
    from the backlog backend (e.g., JIRA).
    """
    try:
        tasks = await backlog_service.get_open_tasks(project_key)
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 4.4. Agent-Side: Calling Tools with `instructor` (New Section)

This code demonstrates the **recommended pattern for the AI agent's client logic**. It uses `instructor` to reliably generate a valid `RAGQuery` object and then calls the server endpoint.

```python
# In the agent's client-side code (NOT on the server)
import instructor
import openai
import requests
from pydantic import BaseModel

# 1. Define the Pydantic model, mirroring the server's API.
#    In a real application, this could even be auto-generated from the
#    server's OpenAPI spec.
class RAGQuery(BaseModel):
    query_text: str
    top_k: int = 5

# 2. Patch the OpenAI client with instructor
client = instructor.patch(openai.OpenAI())

def call_rag_tool_safely(user_prompt: str) -> dict:
    """
    Uses an LLM to reliably generate a valid RAGQuery object and then
    calls the MCP Server's tool endpoint.
    """
    print(f"Agent is thinking about the prompt: '{user_prompt}'")
    
    # 3. Let the LLM generate the structured request object.
    #    `instructor` ensures the output matches the `RAGQuery` model.
    rag_request = client.chat.completions.create(
        model="gpt-4-turbo",
        response_model=RAGQuery, # The magic happens here
        messages=[{"role": "user", "content": f"Based on the user's request, formulate a search query: '{user_prompt}'"}]
    )

    print(f"--> Generated valid request object: {rag_request.model_dump_json(indent=2)}")

    # 4. Call the MCP Server API with the guaranteed-valid data
    response = requests.post(
        "http://localhost:8000/tools/rag-query", # Assume local server
        json=rag_request.model_dump()
    )
    response.raise_for_status() # Raise an exception for bad status codes
    return response.json()

# --- Example Usage in the Agent's main loop ---
user_input = "Find documents about our Kubernetes deployment guidelines"
results = call_rag_tool_safely(user_input)
print(f"--> Received results from MCP Server: {results}")

```

---

## 5. Deployment Strategies

### 5.1. Local Development

For local development, use `uvicorn` to run the FastAPI server with hot-reloading.

1.  **Install dependencies:**
    ```bash
    pip install "fastapi[all]" uvicorn python-multipart PyYAML
    ```
2.  **Run the server:**
    ```bash
    uvicorn main:app --reload
    ```
    The API will be available at `http://127.0.0.1:8000`, and the interactive documentation at `http://127.0.0.1:8000/docs`.

### 5.2. Kubernetes Deployment

Containerizing the application with Docker and deploying to Kubernetes provides scalability and resilience.

**1. `Dockerfile`**

```dockerfile
# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code
COPY . .

# Expose port 80 to the outside world
EXPOSE 80

# Command to run the application using Gunicorn for production
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "main:app", "-b", "0.0.0.0:80"]
```

**2. Kubernetes Deployment (`deployment.yaml`)**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-server-deployment
spec:
  replicas: 2 # Start with 2 replicas for availability
  selector:
    matchLabels:
      app: mcp-server
  template:
    metadata:
      labels:
        app: mcp-server
    spec:
      containers:
      - name: mcp-server
        image: your-repo/mcp-server:latest # Replace with your image
        ports:
        - containerPort: 80
        envFrom:
        - configMapRef:
            name: mcp-server-config
        - secretRef:
            name: mcp-server-secrets
```

**3. Kubernetes Service (`service.yaml`)**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: mcp-server-service
spec:
  selector:
    app: mcp-server
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
  type: ClusterIP # Or LoadBalancer for external access
```

### 5.3. High-Availability (HA)

To achieve high availability:

* **Increase Replicas:** Run at least 3 replicas of the MCP server pod in your Kubernetes deployment.
* **Horizontal Pod Autoscaler (HPA):** Configure an HPA to automatically scale the number of pods based on CPU or memory usage.
* **Stateful Services:** Ensure your RAG backend (Weaviate, Postgres) and any other databases are also deployed in a HA configuration (e.g., using clusters, read replicas).
* **Readiness/Liveness Probes:** Configure health checks in your Kubernetes deployment to ensure traffic is only routed to healthy pods.

---

## 6. Capabilities of a RAG-based MCP Server

A mature MCP Server, combined with a capable agent client, should have the following features:

* **Resource Management:**
    * [x] Versioned access to prompts and templates.
    * [ ] Dynamic configuration management for different environments.
* **Toolbox:**
    * [x] RAG query tool (`rag-query`).
    * [x] RAG ingestion tool (`rag-add` for files, text, URLs).
    * [x] Backlog integration (`get-backlog`, `update-task-status`).
    * [ ] Code repository interaction (`create-repo`, `list-files`, `read-file`).
    * [ ] CI/CD interaction (`trigger-pipeline`, `get-pipeline-status`).
    * [ ] Calendar/Scheduling tool (`find-meeting-times`).
* **State Management:**
    * [ ] A simple database to track the state of long-running agent tasks.
* **Security & Observability:**
    * [ ] API key authentication for agents.
    * [ ] Structured logging to track agent actions and tool usage.
    * [ ] Rate limiting to prevent abuse.
    * [ ] Tracing with tools like OpenTelemetry to monitor performance.

---

## 7. Common Pitfalls and Mitigation

### 7.1. MCP Server Implementation

* **Pitfall: Tight Coupling.** Hardcoding logic for a specific AI agent model or framework.
    * **Mitigation:** Design the server as a generic, model-agnostic API. The agent is just a client.
* **Pitfall: Poor Tool Documentation.** The agent cannot use a tool it doesn't understand.
    * **Mitigation:** **Use FastAPI's auto-documentation.** Write extremely clear, concise docstrings and Pydantic field descriptions. Treat your API documentation as a UI for the agent.
* **Pitfall: Security Risks.** An agent executing tools is a potential security vector. A compromised agent could call `delete-database` if such a tool exists.
    * **Mitigation:** Implement strict authentication and authorization. Tools should follow the **principle of least privilege**. Never expose destructive or overly broad tools without a human-in-the-loop confirmation step.
* **Pitfall: Lack of Versioning.** Changing a prompt or tool signature breaks agents that depend on it.
    * **Mitigation:** Use API versioning (e.g., `/v1/tools/rag-query`). Keep prompts versioned in their resource files.
* **Pitfall: Poor Tool Invocation.** The agent misinterprets how to call a tool, leading to API errors.
    * **Mitigation (Updated):** This is a two-part solution.
        1. **Server-Side:** Use FastAPI's auto-documentation to provide a clear, machine-readable OpenAPI schema.
        2. **Client-Side:** The AI Agent client **must** use a library like `instructor` to consume this schema and generate validated, structured requests. This shifts the burden from the LLM "understanding" documentation to programmatically conforming to a data structure, which is far more reliable.

### 7.2. RAG-based Tool Implementation

* **Pitfall: "Garbage In, Garbage Out".** Indexing low-quality, irrelevant, or poorly formatted documents leads to useless RAG results.
    * **Mitigation:** Implement a robust **ETL (Extract, Transform, Load) pipeline** for document ingestion. Pre-process and clean documents before indexing. Use metadata to filter sources.
* **Pitfall: Suboptimal Chunking.** Document chunks that are too large or too small can hurt retrieval performance.
    * **Mitigation:** Experiment with different chunking strategies (e.g., recursive character splitting, semantic chunking). The optimal strategy depends on the data. A good starting point is ~512-1024 tokens per chunk with some overlap.
* **Pitfall: Stale Information.** The knowledge base becomes outdated.
    * **Mitigation:** Implement a process for periodically re-indexing or updating documents. The `rag-add` tool is part of this solution, but automated crawlers or webhooks can also trigger updates.
* **Pitfall: Ineffective Retrieval.** The agent gets irrelevant results.
    * **Mitigation:** Use a **hybrid search** approach that combines semantic (vector) search with traditional keyword search. This often yields the best of both worlds. Weaviate supports this out of the box.
* **Pitfall: Stale Information.** The knowledge base becomes outdated.
    * **Mitigation:** Implement a process for periodically re-indexing documents, triggered via webhooks or scheduled jobs.
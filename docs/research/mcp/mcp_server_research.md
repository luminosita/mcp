# MCP Server Implementation Report

**Author:** Gemini, Senior Software Engineer
**Date:** October 8, 2025
**Version:** 1.1

**Changelog v1.1:**
* Added research on the "Pydantic AI" pattern for structured LLM output.
* Recommended `instructor` as a key library for the AI Agent's client-side logic.
* Included new implementation examples and architectural considerations for robust agent-to-server communication.

## 1. Executive Summary

This report outlines the research, architecture, and implementation plan for creating a **Multi-purpose Command and Prompting (MCP) Server** in Python. The MCP Server will act as a centralized hub, providing AI agents with standardized tools, versioned prompts, and access to organizational resources.

The core of this proposal is a modular architecture built on **FastAPI**, leveraging a powerful **Retrieval-Augmented Generation (RAG)** backend. We recommend **Weaviate** or **PostgreSQL with `pgvector`** for production RAG backends.

Crucially, this report now also recommends a specific pattern for the **AI Agent's client-side implementation**. The agent's logic should leverage structured output generation (via libraries like **`instructor`**) to ensure reliable, schema-compliant communication with the server's tools, drastically reducing errors and improving overall system robustness.

---

## 2. Introduction: The MCP Server Concept

The MCP Server is an API-driven service designed to be the "brain" and "toolbelt" for AI agents operating within our development ecosystem. It decouples the agent's core logic from the specifics of our internal tools and processes.

**Key Objectives:**

* **Standardization:** Provide a single source of truth for prompts, templates, and operational logic.
* **Tooling:** Expose complex operations as simple, well-documented tools for the agent.
* **Governance:** Enforce development best practices programmatically.
* **Extensibility:** Allow for the easy addition of new tools, resources, and data sources.

---

## 3. Proposed Architecture & Technology Stack

We propose a modular, service-oriented architecture. The core of the server is a FastAPI application, while the AI Agent client is empowered by a structured output library.

![A diagram of the MCP Server Architecture. An AI Agent Client (using Instructor) communicates with a central FastAPI application. The application has modules for Tool Execution, Resource Management, etc., and connects to external services like Git, JIRA, and a Vector Database.](https://i.imgur.com/g8v8pQp.png)

### 3.1. MCP Server Technology

* **API Framework:** **FastAPI**. Chosen for its high performance, native `async` support, Pydantic-based data validation, and automatic generation of OpenAPI documentation, which serves as a machine-readable tool manifest for the agent.
* **RAG Backend (Vector Database):**
    * **Local/Development:** **ChromaDB**.
    * **Production/Staging:** **Weaviate** or **PostgreSQL with `pgvector`**.
* **Data Parsing/Handling:** **Pydantic** for modeling all API requests/responses.

### 3.2. AI Agent Client-Side Technology (New Recommendation)

* **Structured Output Generation:** **`instructor`**. This library patches the OpenAI client to force LLM outputs into a specified Pydantic model. This is not part of the server, but is the recommended way for the agent to interact with the server.
* **Why `instructor`?** It solves the problem of LLM unreliability. Instead of prompting an LLM to "generate JSON in the right format," this pattern guarantees the output conforms to the Pydantic model required by the server's API, including validation and automated retries on failure.

---

## 4. Implementation Guidelines & Examples

### 4.1. Server: FastAPI Setup

```python
# main.py
from fastapi import FastAPI, HTTPException, UploadFile, File
from typing import List
from pydantic import BaseModel, Field

app = FastAPI(
    title="MCP Server",
    description="A server providing tools and resources for AI Agents.",
    version="1.1.0"
)

# --- Pydantic Models (The "Contract" for the Agent) ---
class RAGQuery(BaseModel):
    query_text: str
    top_k: int = 5

class RAGResult(BaseModel):
    source: str
    content: str
    score: float
```

### 4.2. Server: Serving Resources (Prompts)

The server provides standardized prompts to guide the agent.

```python
# main.py (continued)
@app.get("/prompts/{prompt_name}", tags=["Resources"])
def get_prompt(prompt_name: str):
    """Retrieves a versioned prompt template by its name."""
    # ... (logic to load prompt from a file)
    # This endpoint remains unchanged.
```

### 4.3. Server: Implementing Tools

These are the API endpoints the agent will call. The Pydantic models (`RAGQuery`) define the required inputs.

```python
# main.py (continued)
@app.post("/tools/rag-query", response_model=List[RAGResult], tags=["Tools"])
async def rag_query_tool(query: RAGQuery):
    """
    Performs a semantic search against the knowledge base (RAG backend).
    This tool expects a request body conforming to the `RAGQuery` model.
    """
    try:
        # The query object is a validated Pydantic instance
        results = await rag_service.search(query.query_text, top_k=query.top_k)
        return results
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

Deployment strategies for the FastAPI server remain unchanged. It should be containerized with **Docker** and orchestrated with **Kubernetes** for scalability and high-availability. (Details on Dockerfile, Kubernetes YAMLs from the previous report are still applicable).

---

## 6. Capabilities of a RAG-based MCP Server

A mature MCP Server, combined with a capable agent client, should have the following features:

* **Resource Management:** Versioned prompts, templates, and configurations.
* **Toolbox:** RAG tools, backlog integration, code repository interaction, CI/CD triggers.
* **Agent-Side Intelligence (New):**
    * **[x] Robust Tool Usage:** Reliably call server tools using structured output generation (`instructor` pattern).
    * **[ ] Data Extraction:** Parse unstructured text from files or other sources into Pydantic models.
* **Security & Observability:** API key auth, structured logging, rate limiting.

---

## 7. Common Pitfalls and Mitigation

### 7.1. MCP Server & Agent Interaction

* **Pitfall: Poor Tool Invocation.** The agent misinterprets how to call a tool, leading to API errors.
    * **Mitigation (Updated):** This is a two-part solution.
        1. **Server-Side:** Use FastAPI's auto-documentation to provide a clear, machine-readable OpenAPI schema.
        2. **Client-Side:** The AI Agent client **must** use a library like `instructor` to consume this schema and generate validated, structured requests. This shifts the burden from the LLM "understanding" documentation to programmatically conforming to a data structure, which is far more reliable.

* **Pitfall: Security Risks.** An agent executing tools can be a security vector.
    * **Mitigation:** Implement strict auth. Tools should follow the principle of least privilege. Avoid exposing destructive tools without a human-in-the-loop confirmation.

### 7.2. RAG-based Tool Implementation

* **Pitfall: "Garbage In, Garbage Out".** Indexing low-quality documents leads to useless RAG results.
    * **Mitigation:** Implement a robust ETL pipeline for document ingestion. Pre-process and clean documents before indexing.
* **Pitfall: Stale Information.** The knowledge base becomes outdated.
    * **Mitigation:** Implement a process for periodically re-indexing documents, triggered via webhooks or scheduled jobs.
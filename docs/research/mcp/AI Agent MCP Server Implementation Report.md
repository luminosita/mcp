

# **Architecting and Implementing a Production-Grade MCP Server for AI-Driven Software Development**

## **1. Executive Summary & Architectural Vision**

### **1.1. Purpose and Scope**

This report provides a comprehensive architectural blueprint and implementation guide for building a custom Model Context Protocol (MCP) Server in Python. This server will act as the executive backend for an AI agent, empowering it to perform complex software development tasks, thereby accelerating development cycles and automating routine engineering work. The scope of this document covers the system's architecture, a detailed implementation plan with code examples, multi-stage deployment strategies, and an analysis of common implementation pitfalls.

### **1.2. The Core Problem**

AI agents, powered by Large Language Models (LLMs), possess powerful reasoning capabilities but lack direct, secure access to the tools and context of a software development environment. They cannot interact with version control systems like Git, project management tools like JIRA, or CI/CD systems out of the box. The MCP server bridges this critical gap. It acts as a standardized, secure interface layer—the "arms and legs" for the agent's "brain"—translating the agent's abstract plans into concrete actions within the developer ecosystem.[^1]

### **1.3. Proposed System Architecture**

A modular, scalable architecture is proposed, centered around a FastAPI web server that exposes a suite of developer tools via the Model Context Protocol. The system is composed of four primary components:

* **The AI Agent Host:** The application where the AI agent's reasoning loop executes. This could be a custom application, an Integrated Development Environment (IDE) extension, or a platform like GitHub Copilot Agent Mode.[^2] It contains an MCP Client component responsible for discovering and communicating with our server.  
* **The MCP Server Core:** A Python application built with FastAPI and Pydantic. It handles MCP communication over a Streamable HTTP transport, authenticates requests, and routes them to the appropriate tool implementations. This core is the central nervous system of the entire operation.  
* **The Developer Toolkit:** A collection of Python modules, each implementing a specific capability (e.g., JIRA integration, CI/CD manifest generation). These capabilities are exposed as standardized MCP Tool primitives, defined with Pydantic schemas for type-safe, validated inputs and outputs.  
* **The RAG Subsystem:** A specialized component comprising a data ingestion pipeline, a vector database for storing document embeddings, and a query interface. This subsystem is exposed as a single, powerful rag_query tool to the agent, providing it with access to a dynamic knowledge base.

### **1.4. Architectural Diagram**

The proposed architecture facilitates a clear and secure flow of information, separating the agent's reasoning from the execution of tasks.

The primary operational flow is as follows:

1. A user submits a high-level request (e.g., "Review the current backlog for project 'X' and set up a new Git branch for the highest priority feature") to the AI Agent Host.  
2. The Agent's reasoning loop (the "brain") processes the request and determines that it needs to interact with external systems. It formulates a plan that involves calling one or more tools.  
3. The MCP Client within the Host sends a tool/run request over a stateful JSON-RPC 2.0 connection to the MCP Server.[^3] This request specifies the tool name (e.g., retrieve_backlog_items) and its arguments.  
4. The MCP Server Core receives and validates the request against the tool's Pydantic schema. It then invokes the corresponding Python tool function.  
5. The tool function executes its logic, interacting with an external service (e.g., making a REST API call to JIRA).  
6. The result of the tool's execution is packaged into a response and sent back to the AI Agent Host.  
7. The Agent incorporates the tool's output into its context and proceeds to the next step in its plan, which may involve further reasoning or another tool call.

A parallel data ingestion flow for the RAG subsystem operates independently:

1. A user or an automated process uploads a document (e.g., technical documentation, coding standards) to a dedicated REST API endpoint on the server (e.g., POST /rag/upload).  
2. This endpoint triggers a background data pipeline that chunks the document, generates vector embeddings, and stores them in the vector database.  
3. This newly indexed information immediately becomes available to the agent via the rag_query MCP tool.

## **2. The MCP Foundation: Protocol and Design Principles**

### **2.1. Understanding the Model Context Protocol (MCP)**

The Model Context Protocol (MCP) is an open standard, initiated by Anthropic and adopted by major AI providers, designed to create a universal interface between AI applications and external capabilities.[^5] Its primary function is to solve the M×N integration problem, where every LLM-based application would otherwise need a custom integration for every external tool or data source.[^5] It establishes a standardized client-server model communicating over JSON-RPC 2.0, which allows for structured, bi-directional message passing.[^3] 
While often described as a "USB-C port for AI," this analogy understates the protocol's sophistication.[^5] Unlike a simple, stateless REST API, MCP is a stateful protocol that requires lifecycle management, including an initialization sequence to negotiate capabilities between the client and server.[^3] Furthermore, it supports bi-directional communication primitives. For instance, the Elicitation primitive allows a server to request additional information from the user via the client, and the Sampling primitive allows a server to request that the client's host execute an LLM completion.[^3] This stateful, interactive nature elevates the MCP server from a passive library of functions to an active participant in a complex, orchestrated workflow. The architecture must therefore be designed to handle persistent connections and session state, a fundamental departure from typical web service design.

For a production-grade remote server, the protocol specifies transports like Server-Sent Events (SSE) and the more modern Streamable HTTP.[^4] This report will focus on implementing the Streamable HTTP transport, as it provides robust, bi-directional communication over a single HTTP endpoint and is the current recommended standard.[^9] 
### **2.2. Core Primitives**

An MCP server can expose its capabilities through three core primitives. This implementation will leverage all three to provide a rich, flexible interface for the AI agent.[^3] 
* **Tools:** These are functions that the AI agent can execute to perform actions or cause side effects. Tools are the primary mechanism for an agent to interact with the world. Each tool is defined by a name, a detailed description for the LLM's comprehension, and a strict input schema that defines its parameters.[^4] This will be the most heavily utilized primitive in our server, exposing capabilities for JIRA, and more.  
* **Resources:** These represent read-only contextual data that can be provided to the agent. Resources do not execute computations but return information to augment the agent's knowledge.[^4] This primitive is ideal for providing static but important context, such as a file containing the organization's coding standards, API design guidelines, or a manifest of available project templates.  
* **Prompts:** These are reusable prompt templates or workflows that the server can offer to the client.[^4] This powerful feature allows the server to encapsulate complex, multi-step tasks into a single, named prompt. For example, a full_project_setup prompt could guide the agent through a sequence of tool calls: retrieve_backlog_items, initialize_project_repository, and create_kubernetes_manifest. This standardizes complex operations and improves the reliability of the agent.

### **2.3. Technology Stack Justification**

The selection of the technology stack is a critical architectural decision, driven by the goals of developer productivity, performance, type safety, and alignment with the broader AI ecosystem.

* **Python:** As the lingua franca of AI and machine learning, Python offers an unparalleled ecosystem of mature libraries for every required integration, from web frameworks to LLM orchestration and external service clients.[^10] The official MCP SDK for Python provides the necessary building blocks for our server.[^10] 
* **FastAPI:** This high-performance web framework is the ideal foundation for the MCP server core. Its key advantages are its automatic generation of OpenAPI-compliant documentation from code, a powerful dependency injection system, and its native integration with Pydantic.[^12] This tight coupling with Pydantic is not merely a convenience; it is central to building a robust tool server. Emerging libraries like fastapi-mcp even allow for the automatic conversion of standard FastAPI routes into MCP tools, which can dramatically accelerate development by unifying web API and MCP tool definitions.[^13] 
* **Pydantic & Pydantic AI:** The use of Pydantic for all data modeling is non-negotiable for a production-grade system. It enforces strict data validation and type safety at the boundaries of the application. The decision to also leverage Pydantic AI as the agentic framework is strategic. Pydantic AI is explicitly designed to bring the "FastAPI feeling"—a focus on type safety, developer ergonomics, and minimal boilerplate—to agent development.[^16] It uses Pydantic models to define tool schemas and enforce structured outputs from LLMs. Critically, it also has built-in support for acting as an MCP client, allowing it to connect to and consume tools from MCP servers.[^9] 
The combination of FastAPI for the server layer and Pydantic for data validation and tool definition creates a highly synergistic stack. This "Pydantic-first" approach reflects a broader convergence in the Python AI ecosystem, where frameworks like LangChain and LlamaIndex also rely on Pydantic for defining their tool interfaces.[^21] By aligning with this pattern, the architecture maximizes code reuse, ensures end-to-end type safety from the API boundary down to the LLM interaction, and provides a consistent, intuitive developer experience. A tool's input schema can be defined once as a Pydantic model and be automatically validated by FastAPI, correctly schematized for the LLM by the MCP library, and statically type-checked by the IDE. This significantly reduces the potential for runtime errors and simplifies maintenance.

## **3. Core Server Implementation: A Practical Guide**

### **3.1. Project Structure and Setup**

A well-organized project structure is essential for maintainability and scalability. The following structure separates concerns, making it easier to navigate and extend the codebase.

```
/mcp-dev-agent/  
├──.venv/                  # Virtual environment  
├── pyproject.toml          # Project metadata and dependencies  
├── README.md  
├── mcp_server/  
│   ├── __init__.py  
│   ├── main.py             # FastAPI app and MCP server initialization  
│   ├── config.py           # Configuration management (pydantic-settings)  
│   ├── tools/  
│   │   ├── __init__.py  
│   │   ├── base_tools.py  
│   │   ├── jira_tools.py  
│   │   └── cicd_tools.py  
│   └── rag/  
│       ├── __init__.py  
│       ├── pipeline.py     # Data ingestion and processing logic  
│       ├── query.py        # RAG query engine setup  
│       └── vector_store.py # Vector database connection and setup  
└── tests/  
    ├── __init__.py  
    └── test_tools/  
        └── test_base_tools.py
```

Dependencies will be managed using uv, a modern, high-performance Python package manager.[^10] The pyproject.toml file will define all necessary dependencies, including fastapi, uvicorn, mcp-sdk, pydantic, pydantic-settings, and the libraries for each tool.

Configuration, especially for sensitive data like API keys and database URLs, will be handled using pydantic-settings. This library loads configuration from environment variables or a .env file into a typed Pydantic model, ensuring that all required settings are present and correctly formatted at startup.[^23] 
### **3.2. Building the FastAPI Application Shell**

The foundation of the server is a standard FastAPI application. The MCP server logic will be integrated into this application, allowing it to serve both standard HTTP requests (like a health check or the RAG upload endpoint) and handle MCP communication.

The official Python mcp SDK provides the FastMCP class, a high-level interface that simplifies the creation of MCP servers. It uses decorators to register Python functions as MCP tools, automatically handling the underlying protocol complexities.[^10] 
The following code in mcp_server/main.py initializes both the FastAPI app and the FastMCP server. While libraries exist to automatically mount an MCP server onto FastAPI, a manual integration provides more control and clarity. For a production remote server, the streamable-http transport is the correct choice.

```Python

# mcp_server/main.py  
import uvicorn  
from fastapi import FastAPI, Request, Response  
from mcp.server.fastmcp import FastMCP  
from mcp.transport.streamable_http import asgi_app as mcp_asgi_app

from.config import settings  
from.tools import base_tools, jira_tools, cicd_tools  
from.rag import query as rag_query_tool

# 1. Initialize the FastAPI application  
app = FastAPI(  
    title="DevAgent MCP Server",  
    description="A Model Context Protocol server for AI-driven software development tasks.",  
    version="1.0.0"  
)

# 2. Initialize the FastMCP server  
# The tools are automatically registered when their modules are imported  
mcp_server = FastMCP(  
    name="DevAgentToolkit",  
    version="1.0.0"  
)

# 3. Mount the MCP ASGI app onto a specific path in the FastAPI application  
app.mount("/mcp", mcp_asgi_app(mcp_server))

# 4. Add a standard health check endpoint  
@app.get("/health", tags=)  
async def health_check():  
    """Performs a health check of the server."""  
    return {"status": "ok", "mcp_server_name": mcp_server.name}

if __name__ == "__main__":  
    uvicorn.run(  
        "mcp_server.main:app",  
        host="0.0.0.0",  
        port=settings.SERVER_PORT,  
        reload=True  
    )
```

### **3.3. Defining Robust Tools with Pydantic**

A consistent and robust pattern for defining tools is crucial for the reliability of the agent. Every tool will adhere to the following principles:

1. **Decorator-based Registration:** Each tool is an async Python function registered with the @mcp_server.tool() decorator.  
2. **Pydantic for Inputs:** Tool arguments are encapsulated in a pydantic.BaseModel. This provides strong typing, validation, and clear schema definition. The model's fields use Field to provide descriptions, which are essential for the LLM to understand how to use the tool.  
3. **Descriptive Docstrings:** The function's docstring serves as the tool's primary description for the LLM. It must clearly and concisely explain the tool's purpose, its parameters, and when it should be used.[^17] 
The following example of a simple echo tool in mcp_server/tools/base_tools.py demonstrates this pattern.

```Python

# mcp_server/tools/base_tools.py  
from pydantic import BaseModel, Field  
from..main import mcp_server

class EchoInput(BaseModel):  
    """Input model for the echo tool."""  
    message: str = Field(  
       ...,   
        description="The message to be echoed back by the tool."  
    )  
    repeat_count: int = Field(  
        default=1,   
        ge=1,   
        le=10,   
        description="The number of times to repeat the message."  
    )

@mcp_server.tool(  
    name="system.echo",  
    description="A simple tool that echoes a message back. Useful for testing server connectivity and basic functionality."  
)  
async def echo(params: EchoInput) -> str:  
    """  
    Echoes a given message a specified number of times, separated by spaces.

    This tool is primarily for diagnostic purposes to confirm that the MCP  
    client-server communication is working correctly.

    Args:  
        params: The input parameters, including the message and the repeat count.

    Returns:  
        A string containing the repeated message.  
    """  
    return " ".join([params.message] * params.repeat_count)
```

This example showcases the synergy of the chosen technology stack. The EchoInput model ensures that any call to this tool will have a valid message and a repeat_count between 1 and 10. The mcp library introspects this model and the function signature to generate the precise JSON Schema that the MCP protocol requires. The docstring and field descriptions provide the necessary semantic information for the LLM to make an informed decision about using the tool. This pattern creates a self-documenting, type-safe, and reliable tool definition that minimizes boilerplate and runtime errors.

## **4. Implementing the Software Development Toolkit**

This section provides the implementation details for the core tools that empower the AI agent to perform software development tasks. Each tool follows the robust Pydantic-based pattern established previously.

### **4.1. JIRA Integration Tool**

This tool connects the agent to the project management system, allowing it to retrieve backlog items and understand current work priorities.

* **Library:** jira, the official Python library for the JIRA REST API.[^9] 
* **Functionality:** The retrieve_backlog_items tool will connect to a JIRA instance using credentials stored securely in the environment and execute a JIRA Query Language (JQL) search.  
* **Output Structuring:** To provide clean, predictable data to the LLM, the raw API response will be parsed into a list of Pydantic models. This abstracts away the complexity of the full JIRA API response and provides only the essential fields.

```Python

# mcp_server/tools/jira_tools.py  
from typing import List, Optional  
from jira import JIRA  
from pydantic import BaseModel, Field  
from..main import mcp_server  
from..config import settings

class JiraQueryInput(BaseModel):  
    project_key: str = Field(..., description="The key of the JIRA project to search within (e.g., 'PROJ').")  
    jql_filter: str = Field(  
        default="status = 'To Do' ORDER BY priority DESC",  
        description="A JQL filter string to refine the search for issues."  
    )  
    max_results: int = Field(default=10, ge=1, le=50, description="The maximum number of issues to return.")

class JiraIssueOutput(BaseModel):  
    key: str  
    summary: str  
    issue_type: str  
    status: str  
    priority: str  
    description: Optional[str] = None

@mcp_server.tool(  
    name="jira.retrieve_backlog_items",  
    description="Retrieves a list of backlog items (issues) from a specified JIRA project using a JQL query."  
)  
async def retrieve_backlog_items(params: JiraQueryInput) -> List[JiraIssueOutput]:  
    """  
    Fetches issues from a JIRA project based on a JQL query.

    Args:  
        params: Input parameters containing the project key, JQL filter, and max results.

    Returns:  
        A list of structured issue data. Returns an empty list if an error occurs or no issues are found.  
    """  
    try:  
        jira_client = JIRA(  
            server=settings.JIRA_INSTANCE_URL,  
            basic_auth=(settings.JIRA_USERNAME, settings.JIRA_API_TOKEN.get_secret_value())  
        )  
          
        full_jql = f"project = {params.project_key} AND ({params.jql_filter})"  
        issues = jira_client.search_issues(full_jql, maxResults=params.max_results)  
          
        results =  
        for issue in issues:  
            results.append(  
                JiraIssueOutput(  
                    key=issue.key,  
                    summary=issue.fields.summary,  
                    issue_type=issue.fields.issuetype.name,  
                    status=issue.fields.status.name,  
                    priority=issue.fields.priority.name,  
                    description=issue.fields.description  
                )  
            )  
        return results  
    except Exception as e:  
        # In a real system, log the full error  
        print(f"Error retrieving JIRA issues: {e}")  
        return
```

### **4.2. CI/CD Manifest Generation Tool**

This tool automates the creation of standardized deployment artifacts, a repetitive and error-prone task for human developers.

* **Library:** pyyaml for safe YAML generation.  
* **Functionality:** The create_kubernetes_manifest tool will generate the YAML text for a Kubernetes Deployment and Service.  
* **Rationale:** By providing this as a tool, the agent can create deployment configurations that adhere to organizational standards without needing to understand the intricacies of Kubernetes YAML syntax.

```Python

# mcp_server/tools/cicd_tools.py  
import yaml  
from pydantic import BaseModel, Field  
from typing import Literal  
from..main import mcp_server

class K8sManifestInput(BaseModel):  
    app_name: str = Field(..., description="The name of the application (e.g., 'my-awesome-api').")  
    docker_image: str = Field(..., description="The full name and tag of the Docker image to deploy (e.g., 'my-registry/my-app:v1.2.3').")  
    replicas: int = Field(default=2, ge=1, description="The number of pod replicas for the deployment.")  
    container_port: int = Field(..., description="The port the container listens on.")  
    service_type: Literal = Field(default='ClusterIP', description="The type of Kubernetes service to create.")

@mcp_server.tool(  
    name="cicd.create_kubernetes_manifest",  
    description="Generates Kubernetes Deployment and Service YAML manifests for a containerized application."  
)  
async def create_kubernetes_manifest(params: K8sManifestInput) -> str:  
    """  
    Creates standard Kubernetes YAML manifests for deploying an application.

    Args:  
        params: Input parameters defining the application's configuration.

    Returns:  
        A string containing the combined YAML for the Deployment and Service.  
    """  
    labels = {"app": params.app_name}  
      
    deployment = {  
        "apiVersion": "apps/v1",  
        "kind": "Deployment",  
        "metadata": {"name": f"{params.app_name}-deployment", "labels": labels},  
        "spec": {  
            "replicas": params.replicas,  
            "selector": {"matchLabels": labels},  
            "template": {  
                "metadata": {"labels": labels},  
                "spec": {  
                    "containers": [{  
                        "name": params.app_name,  
                        "image": params.docker_image,  
                        "ports": [{"containerPort": params.container_port}]  
                    }]  
                }  
            }  
        }  
    }  
      
    service = {  
        "apiVersion": "v1",  
        "kind": "Service",  
        "metadata": {"name": f"{params.app_name}-service"},  
        "spec": {  
            "selector": labels,  
            "ports":,  
            "type": params.service_type  
        }  
    }  
      
    manifests = [deployment, service]  
    return yaml.dump_all(manifests, sort_keys=False)
```

### **4.3. RAG File Ingestion Endpoint**

This is not an MCP tool but a standard FastAPI endpoint that serves as the entry point to the RAG data pipeline. This architectural separation is deliberate: tool use is for querying and acting, while data ingestion is a separate data management process.

* **Functionality:** The /rag/upload endpoint accepts a file upload. It then triggers a background task to process the file, preventing the HTTP request from blocking during the potentially long-running ingestion process.

```Python

# In mcp_server/main.py, add the following:  
from fastapi import UploadFile, File, BackgroundTasks  
from.rag import pipeline as rag_pipeline

@app.post("/rag/upload", tags=)  
async def upload_file_for_rag_indexing(  
    background_tasks: BackgroundTasks,  
    file: UploadFile = File(...)  
):  
    """  
    Uploads a file to be indexed into the RAG knowledge base.  
    The processing (chunking, embedding, storing) is done in the background.  
    """  
    # Save the file temporarily to pass its path to the background task  
    with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as tmp:  
        shutil.copyfileobj(file.file, tmp)  
        tmp_path = tmp.name

    background_tasks.add_task(rag_pipeline.process_and_index_file, tmp_path)  
      
    return {  
        "filename": file.filename,  
        "content_type": file.content_type,  
        "message": "File accepted and scheduled for indexing."  
    }
```

This design ensures the API is responsive and robust. The agent can be given a tool to *check the status* of an indexing job, but the ingestion itself is handled by a dedicated, asynchronous data pipeline, which is a much more scalable and reliable pattern.

## **5. Architecting and Integrating the RAG Tool**

A Retrieval-Augmented Generation (RAG) system is not merely a tool; it is a complex data engineering subsystem. Its effectiveness hinges on the quality of its data pipeline and the performance of its retrieval mechanism. Failures in RAG systems are most often rooted in data quality and retrieval logic, such as missing content, suboptimal ranking, and context limitations.[^30] Therefore, designing this subsystem requires the same rigor as any other data-intensive application.

### **5.1. RAG Subsystem Architecture**

The RAG subsystem consists of two distinct pipelines:

1. **Ingestion Pipeline:** This is an asynchronous, multi-step process triggered by the /rag/upload endpoint.  
   * **Document Loading:** The raw file (e.g., PDF, Markdown) is loaded into memory.  
   * **Text Splitting (Chunking):** The document is divided into smaller, semantically meaningful chunks. The chunking strategy is critical; chunks that are too small may lack context, while chunks that are too large can introduce noise.[^32] 
   * **Embedding:** Each chunk is converted into a high-dimensional vector representation using an embedding model (e.g., OpenAI's text-embedding-3-small).  
   * **Vector Storage:** The chunks and their corresponding vector embeddings are stored in a specialized vector database.  
2. **Query Pipeline:** This process is encapsulated within the rag_query MCP tool and is executed at runtime.  
   * **Query Embedding:** The user's natural language query is converted into a vector using the same embedding model.  
   * **Similarity Search:** The vector database is queried to find the document chunks whose embeddings are most similar (e.g., by cosine similarity) to the query embedding.  
   * **Context Formulation:** The content of the top-k retrieved chunks is concatenated to form a context string.  
   * **Response Generation:** This context string is returned by the tool to the AI agent, which then uses it along with the original query to generate a final, knowledge-grounded answer.

### **5.2. Vector Database Selection: A Critical Decision**

The choice of vector database is a pivotal architectural decision with long-term implications for performance, scalability, operational complexity, and cost. The primary choice is between using a general-purpose database with vector capabilities, like PostgreSQL with the pgvector extension, or a specialized, purpose-built vector database.[^33] 
A unified data architecture using pgvector allows vector embeddings to live alongside relational metadata in a single, ACID-compliant database. This simplifies the tech stack, reduces operational overhead, and enables powerful queries that combine semantic search with traditional SQL filtering.[^33] For datasets up to tens or even hundreds of millions of vectors, pgvector offers competitive performance and a superior total cost of ownership.[^33] 
Conversely, dedicated vector databases (whether self-hosted like Qdrant and Weaviate, or fully managed like Pinecone) are optimized from the ground up for high-dimensional vector search. They often provide superior performance at massive scale (billions of vectors), higher query throughput, and more advanced features like quantization and specialized indexing algorithms.[^33] However, they introduce a separate system to deploy, manage, and secure.

For this implementation, **PostgreSQL with pgvector is the recommended choice.** It represents a pragmatic, cost-effective, and architecturally simpler solution that is more than sufficient for the vast majority of enterprise RAG use cases. The following table provides a decision matrix for evaluating self-hosted alternatives if future scale demands it.

| Feature | PostgreSQL with pgvector | Qdrant | Weaviate |
| :---- | :---- | :---- | :---- |
| **Architecture** | Extension to a relational database (OLTP) | Purpose-built vector search engine written in Rust | Vector database with a graph-like data model, written in Go |
| **Key Strengths** | Unified data store (vectors + relational data), ACID compliance, mature ecosystem, powerful SQL + vector queries. | Performance-focused, memory-efficient, advanced filtering, quantization support, clear API. | Built-in vectorization modules, GraphQL API, hybrid search, schema-based data modeling. |
| **Operational Overhead** | Low (if already using PostgreSQL). Requires database tuning. | Moderate. Can be run as a single binary or a distributed cluster. | Moderate to High. Can be complex to set up and scale for production. |
| **Scalability** | Excellent for small to medium scale (millions to tens of millions of vectors). Scaling relies on PostgreSQL's capabilities. | High. Designed for horizontal scaling and large-scale deployments. | High. Designed for horizontal scaling with replication and sharding. |
| **Licensing** | PostgreSQL License (liberal) | Apache 2.0 | BSD 3-Clause |
| **Best For** | Applications needing tight integration between vector search and existing relational data; cost-sensitive projects. | Performance-critical applications; systems requiring advanced filtering and memory optimization. | Complex, multi-modal RAG systems; applications benefiting from a graph-based data structure. |

### **5.3. Implementing the rag_query Tool with LlamaIndex**

LlamaIndex is a data-centric framework specifically designed for building context-augmented LLM applications like RAG.[^36] Its strengths lie in its vast array of data connectors and its focus on the indexing and retrieval pipeline, making it an excellent choice for our RAG subsystem. It also has an official MCP integration package, llama-index-tools-mcp, demonstrating strong alignment with our chosen protocol.[^38] 
The implementation involves configuring LlamaIndex to use our pgvector database and then wrapping its query engine in an MCP tool.

```Python

# mcp_server/rag/query.py  
import asyncpg  
from llama_index.core import VectorStoreIndex, StorageContext  
from llama_index.vector_stores.postgres import PGVectorStore  
from..main import mcp_server  
from..config import settings

# This function would be called during server startup to prepare the query engine  
async def get_rag_query_engine():  
    """Initializes and returns the RAG query engine."""  
    # Ensure the database exists  
    conn = await asyncpg.connect(user=settings.DB_USER, password=settings.DB_PASSWORD.get_secret_value(), host=settings.DB_HOST, port=settings.DB_PORT)  
    await conn.execute(f"CREATE DATABASE {settings.DB_NAME} OWNER {settings.DB_USER}")  
    await conn.close()

    # Connection string for LlamaIndex  
    connection_string = str(settings.DATABASE_URL)  
      
    vector_store = PGVectorStore.from_params(  
        database=settings.DB_NAME,  
        host=settings.DB_HOST,  
        port=settings.DB_PORT,  
        user=settings.DB_USER,  
        password=settings.DB_PASSWORD.get_secret_value(),  
        table_name="rag_documents",  
        embed_dim=1536  # Corresponds to text-embedding-3-small  
    )  
      
    storage_context = StorageContext.from_defaults(vector_store=vector_store)  
    index = VectorStoreIndex.from_vector_store(vector_store)  
      
    return index.as_query_engine(similarity_top_k=3, streaming=False)

# This assumes the query engine is initialized and available globally  
# In a real FastAPI app, this would be managed via dependency injection or a startup event  
# For simplicity, we'll assume it's created and assigned to a global variable.  
# query_engine = await get_rag_query_engine() # This would be run in an async startup event

@mcp_server.tool(  
    name="knowledge.rag_query",  
    description="Queries the internal knowledge base of indexed documents for relevant information. Use this to answer questions about internal processes, technical documentation, or coding standards."  
)  
async def rag_query(query: str) -> str:  
    """  
    Performs a semantic search over the indexed document knowledge base.

    Args:  
        query: The natural language query to search for.

    Returns:  
        A string containing the most relevant context retrieved from the knowledge base.  
    """  
    # In a real app, the query_engine would be accessed from the app's state or a dependency  
    # For this example, we re-initialize it. This is not efficient for production.  
    query_engine = await get_rag_query_engine()  
      
    response = await query_engine.aquery(query)  
      
    # Format the response to be clean context for the LLM  
    context_str = "\n\n---\n\n".join([r.get_text() for r in response.source_nodes])  
    return context_str
```

This implementation provides a powerful, context-aware tool for the agent. The complexity of the RAG pipeline is completely abstracted away behind a simple, natural language interface.

## **6. Deployment and Operationalization**

Deploying the MCP server requires a strategy that progresses from a simple local setup to a robust, scalable, and highly available production environment.

### **6.1. Local Development with Docker Compose**

For a consistent and reproducible local development environment, Docker Compose is the ideal tool. It allows developers to spin up the entire application stack with a single command.

The docker-compose.yml file will define two services:

1. **mcp-server**: The FastAPI application, with the project directory mounted as a volume to enable hot-reloading for rapid development.  
2. **postgres**: A PostgreSQL instance running an image that includes the pgvector extension. A volume is used to persist database data across container restarts.

```yaml

# docker-compose.yml  
version: '3.8'

services:  
  postgres:  
    image: pgvector/pgvector:pg16  
    container_name: mcp_postgres  
    environment:  
      - POSTGRES_DB=${DB_NAME}  
      - POSTGRES_USER=${DB_USER}  
      - POSTGRES_PASSWORD=${DB_PASSWORD}  
    ports:  
      - "${DB_PORT}:5432"  
    volumes:  
      - postgres_data:/var/lib/postgresql/data  
    healthcheck:  
      test:  
      interval: 5s  
      timeout: 5s  
      retries: 5

  mcp-server:  
    build:  
      context:.  
      dockerfile: Dockerfile  
      target: development # Use the development stage from the Dockerfile  
    container_name: mcp_server  
    depends_on:  
      postgres:  
        condition: service_healthy  
    ports:  
      - "${SERVER_PORT}:8000"  
    volumes:  
      -./mcp_server:/app/mcp_server  
    env_file:  
      -.env  
    command: ["uvicorn", "mcp_server.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

volumes:  
  postgres_data:

```

### **6.2. Production Deployment on Kubernetes**

Kubernetes is the de-facto standard for deploying and scaling containerized applications in production.[^39] The deployment process involves containerizing the application and defining its desired state using Kubernetes manifest files.

#### **6.2.1. Dockerfile Optimization**

A multi-stage Dockerfile is a best practice for creating lean and secure production images. The first builder stage installs dependencies into a virtual environment. The final production stage copies only the application code and the pre-built virtual environment into a minimal base image, excluding build tools and development dependencies.[^40] 

```dockerfile
# Dockerfile

# 1. Builder Stage: Installs dependencies  
FROM python:3.12-slim as builder  
WORKDIR /app  
RUN pip install uv  
COPY pyproject.toml uv.lock*./  
RUN uv sync --system

# 2. Development Stage (for local Docker Compose)  
FROM builder as development  
WORKDIR /app  
COPY..  
CMD ["uvicorn", "mcp_server.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# 3. Production Stage: Creates the final, slim image  
FROM python:3.12-slim as production  
WORKDIR /app  
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages  
COPY --from=builder /usr/local/bin /usr/local/bin  
COPY./mcp_server./mcp_server  
EXPOSE 8000  
CMD ["uvicorn", "mcp_server.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### **6.2.2. Kubernetes Manifests**

A set of YAML files will define the resources required to run the application in a Kubernetes cluster.

* **deployment.yaml**: Describes the desired state for the application pods, including the container image, number of replicas, resource requests and limits, and references to configuration and secrets.  
* **service.yaml**: Creates a stable network endpoint to expose the application pods within the cluster.  
* **configmap.yaml**: Stores non-sensitive configuration data, such as the JIRA instance URL.  
* **secret.yaml**: Stores sensitive data, such as API tokens and database credentials. This should be managed with a more secure secret management tool like HashiCorp Vault or a cloud provider's secret manager in a real production environment.

### **6.3. High Availability (HA) Strategy**

Ensuring high availability requires designing the system to be resilient to failures at both the application and infrastructure levels.

* **Stateless Server Pods:** The MCP server application is designed to be stateless. All persistent state is externalized to the PostgreSQL database. This is a critical design choice that allows us to run multiple identical replicas of the server pod behind a load balancer, providing both redundancy and scalability.[^40] If one pod fails, traffic is automatically routed to the healthy replicas.  
* **Horizontal Pod Autoscaler (HPA):** To handle variable loads, an HPA manifest will be configured. The HPA will monitor metrics like CPU and memory utilization and automatically increase or decrease the number of server pods to meet demand.  
* **Liveness and Readiness Probes:** The Deployment manifest will include liveness and readiness probes that target the /health endpoint.  
  * **Readiness Probe:** Kubernetes uses this to determine when a pod is ready to start accepting traffic. If the probe fails, the pod is removed from the service's load balancing pool.  
  * **Liveness Probe:** Kubernetes uses this to check if a running pod is still healthy. If the probe fails repeatedly, Kubernetes will restart the container, helping to recover from deadlocks or unresponsive states.  
* **Database High Availability:** The single point of failure in this architecture is the database. For a true HA production deployment, a single PostgreSQL container is insufficient. The recommended strategy is to use a managed cloud database service (e.g., Amazon RDS, Google Cloud SQL, Azure Database for PostgreSQL). These services provide automated failover, replication, backups, and scaling, offloading the significant operational burden of managing a stateful, highly available database.

## **7. Advanced Topics: Pitfalls, Security, and Best Practices**

### **7.1. Common MCP Server Implementation Pitfalls**

Building a robust MCP server involves more than just exposing functions. Several common pitfalls can compromise security, reliability, and usability.

* **Insecure Tool Design:** A primary risk is exposing tools that can execute arbitrary code or shell commands without rigorous sandboxing.[^8] An agent could be manipulated through prompt injection to execute malicious commands.  
  * **Mitigation:** The server must run in a container with minimal privileges (e.g., as a non-root user). All inputs to tools that interact with the filesystem or execute subprocesses must be strictly validated and sanitized. Never construct shell commands by concatenating unsanitized input from the agent.  
* **Ignoring Protocol State:** Developers accustomed to stateless REST APIs may incorrectly treat the MCP connection as stateless. The MCP protocol requires a specific initialize handshake to negotiate capabilities, and failing to handle this lifecycle correctly will result in a non-functional server.[^3] 
  * **Mitigation:** Rely on a mature MCP server library like the official Python SDK's FastMCP, which correctly implements the protocol's stateful lifecycle management.  
* **Vague or Ambiguous Tool Descriptions:** The LLM's ability to use tools effectively is entirely dependent on the quality of their descriptions (the function docstrings). If a description is unclear, the agent will fail to select the correct tool or will provide incorrect arguments.  
  * **Mitigation:** Write tool descriptions from the perspective of the LLM. Be explicit about what the tool does, what each parameter represents, and provide clear examples of when it should be used. Test and iterate on descriptions as if they were user-facing documentation.  
* **Poor Error Handling:** Simply allowing a Python exception to propagate and return a stack trace to the agent is unhelpful. The agent lacks the context to parse a stack trace and cannot self-correct.  
  * **Mitigation:** Implement comprehensive try...except blocks within each tool function. Catch specific exceptions and return a clear, human-readable error message that explains what went wrong. This provides the agent with actionable feedback it can use to retry the operation with different parameters or formulate a new plan.

### **7.2. Common RAG System Pitfalls and Mitigations**

RAG systems are powerful but brittle. Their failures often fall into predictable categories, as identified by research into RAG failure points.[^32] 
1. **Missing Content (FP1):** The knowledge base does not contain the answer to the query. The system may hallucinate or return a generic "I don't know" response.  
   * **Mitigation:** Implement a feedback loop. When the agent or a user identifies a question that cannot be answered, this should be logged. These logs can be used to create a backlog of content to be added to the knowledge base, creating a virtuous cycle of improvement.  
2. **Missed Top-K Retrieval (FP2):** The correct information exists in the vector database but is not ranked highly enough to be included in the retrieved context passed to the LLM.  
   * **Mitigation:** This is a retrieval quality issue. Strategies include: tuning the number of documents to retrieve (top_k), implementing a two-stage retrieval process with a lightweight first-pass retriever and a more powerful re-ranker model, and using hybrid search techniques that combine semantic (vector) search with traditional keyword search (e.g., BM25).  
3. **Context Window Overflow (FP3):** The system retrieves too many relevant documents, and the combined context exceeds the LLM's context window limit, causing crucial information to be truncated.  
   * **Mitigation:** Employ context compression techniques to summarize less relevant parts of the retrieved documents. For very large contexts, use advanced chaining strategies like Map-Reduce (summarize each document individually, then summarize the summaries) or Refine (iteratively update an answer by processing one document at a time).  
4. **Failure to Extract (FP4):** The correct answer is present in the provided context, but the LLM fails to extract it, often due to excessive noise or contradictory information in the context.  
   * **Mitigation:** Improve the data cleaning and chunking process during ingestion to create cleaner, more focused document chunks. In the query pipeline, preprocess the retrieved context to remove boilerplate or irrelevant text before passing it to the LLM. Prompt engineering can also help by explicitly instructing the model to focus on specific parts of the context.  
5. **Wrong Format (FP5):** The LLM generates the correct information but in an incorrect format (e.g., prose instead of a requested JSON object or list).  
   * **Mitigation:** Use LLMs with strong tool-calling or function-calling capabilities. Define the desired output structure using a Pydantic model and pass its JSON schema to the model, instructing it to generate an output that conforms to the schema.  
6. **Incorrect Specificity (FP6):** The answer is technically correct but is either too general or too specific to be useful for the user's query.  
   * **Mitigation:** Implement a query transformation layer. Before performing the RAG search, use an LLM to analyze the user's query and, if it is ambiguous, rewrite it into a more specific and answerable question.  
7. **Incomplete Answers (FP7):** For multi-part questions, the LLM only addresses one part, even if the context contains information for all parts.  
   * **Mitigation:** Implement a query decomposition step. Use an LLM to break down a complex, multi-part question into several simpler, standalone sub-questions. Execute the RAG pipeline for each sub-question and then synthesize the individual answers into a comprehensive final response.

### **7.3. Observability and Monitoring**

For a production system, robust observability is not optional. It is essential for debugging, performance tuning, and understanding agent behavior.

* **Logging:** Implement structured logging (e.g., JSON format) for every tool invocation. Logs should include a unique request ID, the tool name, the input parameters, the final output, and the execution duration.  
* **Tracing:** Integrate an OpenTelemetry-compatible distributed tracing solution. This allows tracing a single request as it flows from the MCP server, through the execution of a tool, to any downstream API calls (e.g., to JIRA), and back. Frameworks like Pydantic AI offer tight integration with tracing platforms like Pydantic Logfire, which can provide deep insights into agent behavior.[^17] 
* **Metrics:** Expose key performance indicators (KPIs) in a Prometheus-compatible format. Essential metrics include:  
  * Tool call latency (per tool).  
  * Tool call error rate (per tool).  
  * RAG retrieval scores and latency.  
  * Request throughput and API latency.  
    These metrics can be scraped by Prometheus and visualized in Grafana to create dashboards for monitoring system health and performance.

## **8. Essential Features Checklist and Future Roadmap**

### **8.1. V1.0 Essential Features Checklist**

A successful version 1.0 of this MCP server should focus on establishing a robust foundation. The following checklist outlines the minimum viable features for a production-ready deployment.

* [ ] **Security:** Secure, token-based authentication is implemented for all endpoints, including the MCP server path.  
* [ ] **Observability:** Structured logging for all tool calls is in place.  
* [ ] **Testing:** A comprehensive suite of unit and integration tests covers all implemented tools, ensuring their correctness and reliability.  
* [ ] **Deployment:** Complete, version-controlled Kubernetes manifests for the application are created and tested.  
* [ ] **RAG:** A functional RAG pipeline is implemented, including the file upload endpoint and the rag_query tool.  
* [ ] **Core Toolkit:** At least one core software development tool (e.g., jira.retrieve_backlog_items) is fully implemented and tested.  
* [ ] **Health Probes:** A /health endpoint is implemented and configured in the Kubernetes deployment for liveness and readiness probes.

### **8.2. Future Roadmap (V2.0 and Beyond)**

Once the V1.0 foundation is stable, the system can be evolved to support more advanced agentic capabilities and improve performance.

* **Advanced Orchestration:** The current architecture serves tools to a single agent. A significant evolution would be to transform the server into a multi-agent orchestrator. By leveraging agentic frameworks like LangGraph or Pydantic AI's graph support, the server could host and execute complex workflows composed of multiple specialized agents.[^17] For example, a "Code Generation" workflow could be exposed as a single MCP tool, which internally orchestrates a "Planner" agent, a "Coder" agent, and a "Tester" agent. This aligns with the trend of agentic frameworks providing higher-level, composable orchestration patterns.  
* **Caching Layer:** For deterministic tools that are called frequently with the same arguments (e.g., fetching a static configuration file), implementing a caching layer with a technology like Redis can significantly reduce latency and offload work from downstream systems.  
* **Human-in-the-Loop:** For sensitive or high-impact operations (e.g., deploying to production, deleting a repository), it is critical to introduce a human-in-the-loop approval step. This can be implemented by having the tool enter a "pending" state and send a notification (e.g., via Slack or email) to a human operator. The tool would only complete its execution after receiving an explicit approval.[^17] 
* **Expanded Tool Library:** The value of the MCP server is directly proportional to the breadth and power of its toolset. A continuous effort should be made to add new tools that cover more of the software development lifecycle, such as interacting with CI/CD systems (e.g., triggering a GitHub Actions workflow), performing static code analysis, or managing cloud infrastructure via an infrastructure-as-code tool.  
* **Self-Improving RAG:** The RAG system can be made more intelligent by implementing a feedback mechanism. The agent could be prompted to rate the relevance of the documents retrieved by the rag_query tool. This feedback data can be collected and used to periodically fine-tune the embedding model or the re-ranking model, leading to a system that improves its retrieval accuracy over time.

#### **Works cited**

[^1]: Your Architecture vs. AI Agents: Can MCP Hold the Line? - QueryPie, accessed October 8, 2025, [https://www.querypie.com/resources/discover/white-paper/22/your-architect-vs-ai-agents](https://www.querypie.com/resources/discover/white-paper/22/your-architect-vs-ai-agents)  
[^2]: Build Agents using Model Context Protocol on Azure | Microsoft Learn, accessed October 8, 2025, [https://learn.microsoft.com/en-us/azure/developer/ai/intro-agents-mcp](https://learn.microsoft.com/en-us/azure/developer/ai/intro-agents-mcp)  
[^3]: Architecture overview - Model Context Protocol, accessed October 8, 2025, [https://modelcontextprotocol.io/docs/concepts/architecture](https://modelcontextprotocol.io/docs/concepts/architecture)  
[^4]: What is Model Context Protocol (MCP)? - IBM, accessed October 8, 2025, [https://www.ibm.com/think/topics/model-context-protocol](https://www.ibm.com/think/topics/model-context-protocol)  
[^5]: Building AI Agents? A2A vs. MCP Explained Simply - KDnuggets, accessed October 8, 2025, [https://www.kdnuggets.com/building-ai-agents-a2a-vs-mcp-explained-simply](https://www.kdnuggets.com/building-ai-agents-a2a-vs-mcp-explained-simply)  
[^6]: Model Context Protocol - Wikipedia, accessed October 8, 2025, [https://en.wikipedia.org/wiki/Model_Context_Protocol](https://en.wikipedia.org/wiki/Model_Context_Protocol)  
[^7]: Model context protocol (MCP) - OpenAI Agents SDK, accessed October 8, 2025, [https://openai.github.io/openai-agents-python/mcp/](https://openai.github.io/openai-agents-python/mcp/)  
[^8]: Specification - Model Context Protocol, accessed October 8, 2025, [https://modelcontextprotocol.io/specification/latest](https://modelcontextprotocol.io/specification/latest)  
[^9]: Client - Pydantic AI, accessed October 8, 2025, [https://ai.pydantic.dev/mcp/client/](https://ai.pydantic.dev/mcp/client/)  
[^10]: How to build a simple agentic AI server with MCP | Red Hat Developer, accessed October 8, 2025, [https://developers.redhat.com/articles/2025/08/12/how-build-simple-agentic-ai-server-mcp](https://developers.redhat.com/articles/2025/08/12/how-build-simple-agentic-ai-server-mcp)  
[^11]: Model Context Protocol - GitHub, accessed October 8, 2025, [https://github.com/modelcontextprotocol](https://github.com/modelcontextprotocol)  
[^12]: FastAPI, accessed October 8, 2025, [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)  
[^13]: FastAPI-MCP: Simplifying the Integration of FastAPI with AI Agents - InfoQ, accessed October 8, 2025, [https://www.infoq.com/news/2025/04/fastapi-mcp/](https://www.infoq.com/news/2025/04/fastapi-mcp/)  
[^14]: Building an MCP Server with FastAPI and FastMCP - Speakeasy, accessed October 8, 2025, [https://www.speakeasy.com/mcp/building-servers/building-fastapi-server](https://www.speakeasy.com/mcp/building-servers/building-fastapi-server)  
[^15]: alamkanak/fastapi-mcp-openapi: A FastAPI library that provides Model Context Protocol (MCP) tools for endpoint introspection and OpenAPI documentation. This library allows AI agents to discover and understand your FastAPI endpoints through MCP. - GitHub, accessed October 8, 2025, [https://github.com/alamkanak/fastapi-mcp-openapi](https://github.com/alamkanak/fastapi-mcp-openapi)  
[^16]: Agentic AI with Pydantic-AI Part 1. - Han's XYZ, accessed October 8, 2025, [https://han8931.github.io/pydantic-ai/](https://han8931.github.io/pydantic-ai/)  
[^17]: pydantic/pydantic-ai: GenAI Agent Framework, the Pydantic way - GitHub, accessed October 8, 2025, [https://github.com/pydantic/pydantic-ai](https://github.com/pydantic/pydantic-ai)  
[^18]: Understanding Pydantic-AI: A Powerful Alternative to LangChain and LlamaIndex (Part: 1), accessed October 8, 2025, [https://tech.appunite.com/posts/understanding-pydantic-ai-a-powerful-alternative-to-lang-chain-and-llama-index](https://tech.appunite.com/posts/understanding-pydantic-ai-a-powerful-alternative-to-lang-chain-and-llama-index)  
[^19]: Pydantic AI Integration | Heroku Dev Center, accessed October 8, 2025, [https://devcenter.heroku.com/articles/ai-integrations-pydantic](https://devcenter.heroku.com/articles/ai-integrations-pydantic)  
[^20]: Model Context Protocol (MCP) - Pydantic AI, accessed October 8, 2025, [https://ai.pydantic.dev/mcp/overview/](https://ai.pydantic.dev/mcp/overview/)  
[^21]: LangChain vs LangGraph vs LlamaIndex: Which LLM framework should you choose for multi-agent systems? - Xenoss, accessed October 8, 2025, [https://xenoss.io/blog/langchain-langgraph-llamaindex-llm-frameworks](https://xenoss.io/blog/langchain-langgraph-llamaindex-llm-frameworks)  
[^22]: Mcp - LlamaIndex, accessed October 8, 2025, [https://developers.llamaindex.ai/python/framework-api-reference/tools/mcp/](https://developers.llamaindex.ai/python/framework-api-reference/tools/mcp/)  
[^23]: A Fun PydanticAI Example For Automating Your Life - Christopher Samiullah, accessed October 8, 2025, [https://christophergs.com/blog/pydantic-ai-example-github-actions](https://christophergs.com/blog/pydantic-ai-example-github-actions)  
[^24]: Using LangChain With Model Context Protocol (MCP) | by Cobus Greyling - Medium, accessed October 8, 2025, [https://cobusgreyling.medium.com/using-langchain-with-model-context-protocol-mcp-e89b87ee3c4c](https://cobusgreyling.medium.com/using-langchain-with-model-context-protocol-mcp-e89b87ee3c4c)  
[^25]: Function Tools - Pydantic AI, accessed October 8, 2025, [https://ai.pydantic.dev/tools/](https://ai.pydantic.dev/tools/)  
[^26]: Automating some git commands with Python - GeeksforGeeks, accessed October 8, 2025, [https://www.geeksforgeeks.org/python/automating-some-git-commands-with-python/](https://www.geeksforgeeks.org/python/automating-some-git-commands-with-python/)  
[^27]: How to Use Python Jira Library to Retrieve Data - Atlassian Community, accessed October 8, 2025, [https://community.atlassian.com/forums/Jira-articles/How-to-Use-Python-Jira-Library-to-Retrieve-Data/ba-p/2935853](https://community.atlassian.com/forums/Jira-articles/How-to-Use-Python-Jira-Library-to-Retrieve-Data/ba-p/2935853)  
[^28]: jira - PyPI, accessed October 8, 2025, [https://pypi.org/project/jira/](https://pypi.org/project/jira/)  
[^29]: How to fetch data from Jira in Python? - GeeksforGeeks, accessed October 8, 2025, [https://www.geeksforgeeks.org/python/how-to-fetch-data-from-jira-in-python/](https://www.geeksforgeeks.org/python/how-to-fetch-data-from-jira-in-python/)  
[^30]: Overcoming RAG Challenges: Common Pitfalls and How to Avoid Them Introduction, accessed October 8, 2025, [https://www.strative.ai/blogs/overcoming-rag-challenges-common-pitfalls-and-how-to-avoid-them-introduction](https://www.strative.ai/blogs/overcoming-rag-challenges-common-pitfalls-and-how-to-avoid-them-introduction)  
[^31]: Top Problems with RAG systems and ways to mitigate them - AIMon Labs, accessed October 8, 2025, [https://www.aimon.ai/posts/top_problems_with_rag_systems_and_ways_to_mitigate_them/](https://www.aimon.ai/posts/top_problems_with_rag_systems_and_ways_to_mitigate_them/)  
[^32]: Seven Failure Points When Engineering a Retrieval Augmented Generation System - arXiv, accessed October 8, 2025, [https://arxiv.org/html/2401.05856v1](https://arxiv.org/html/2401.05856v1)  
[^33]: PostgreSQL as a Vector Database: A Complete Guide - Airbyte, accessed October 8, 2025, [https://airbyte.com/data-engineering-resources/postgresql-as-a-vector-database](https://airbyte.com/data-engineering-resources/postgresql-as-a-vector-database)  
[^34]: PostgreSQL vector search guide: Everything you need to know about pgvector - Northflank, accessed October 8, 2025, [https://northflank.com/blog/postgresql-vector-search-guide-with-pgvector](https://northflank.com/blog/postgresql-vector-search-guide-with-pgvector)  
[^35]: Vector Databases vs. PostgreSQL with pg_vector for RAG Setups - DEV Community, accessed October 8, 2025, [https://dev.to/simplr_sh/vector-databases-vs-postgresql-with-pgvector-for-rag-setups-1lg2](https://dev.to/simplr_sh/vector-databases-vs-postgresql-with-pgvector-for-rag-setups-1lg2)  
[^36]: Llamaindex vs Langchain: What's the difference? - IBM, accessed October 8, 2025, [https://www.ibm.com/think/topics/llamaindex-vs-langchain](https://www.ibm.com/think/topics/llamaindex-vs-langchain)  
[^37]: LlamaIndex vs LangChain: Which Framework Is Best for Agentic AI Workflows? - ZenML, accessed October 8, 2025, [https://www.zenml.io/blog/llamaindex-vs-langchain](https://www.zenml.io/blog/llamaindex-vs-langchain)  
[^38]: llama-index-tools-mcp · PyPI, accessed October 8, 2025, [https://pypi.org/project/llama-index-tools-mcp/](https://pypi.org/project/llama-index-tools-mcp/)  
[^39]: Deploy Python Apps on Kubernetes and Prepare for Scale — Senthil Kumaran (PyBay 2024) - YouTube, accessed October 8, 2025, [https://www.youtube.com/watch?v=QCeEv0pIHhg](https://www.youtube.com/watch?v=QCeEv0pIHhg)  
[^40]: Deploying a FastAPI application on a local cluster of Kubernetes -, accessed October 8, 2025, [https://safuente.com/deploy-fastapi-local-cluster-kubernetes/](https://safuente.com/deploy-fastapi-local-cluster-kubernetes/)  
[^41]: Seven Ways Your RAG System Could be Failing and How to Fix Them - Label Studio, accessed October 8, 2025, [https://labelstud.io/blog/seven-ways-your-rag-system-could-be-failing-and-how-to-fix-them/](https://labelstud.io/blog/seven-ways-your-rag-system-could-be-failing-and-how-to-fix-them/)  
[^42]: Build Advanced LLM Agents with Pydantic AI & Logfire|Part3 - YouTube, accessed October 8, 2025, [https://www.youtube.com/watch?v=YjUttWnCqC4](https://www.youtube.com/watch?v=YjUttWnCqC4)  
[^43]: lastmile-ai/mcp-agent: Build effective agents using Model ... - GitHub, accessed October 8, 2025, [https://github.com/lastmile-ai/mcp-agent](https://github.com/lastmile-ai/mcp-agent)  
[^44]: Multi-agent AI system in Google Cloud | Cloud Architecture Center, accessed October 8, 2025, [https://cloud.google.com/architecture/multiagent-ai-system](https://cloud.google.com/architecture/multiagent-ai-system)  
[^45]: 7 Practical Design Patterns for Agentic Systems - MongoDB, accessed October 8, 2025, [https://www.mongodb.com/resources/basics/artificial-intelligence/agentic-systems](https://www.mongodb.com/resources/basics/artificial-intelligence/agentic-systems)
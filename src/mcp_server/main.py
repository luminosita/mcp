"""
FastAPI application entry point.

Defines the main FastAPI application instance and configuration.
"""

from fastapi import FastAPI

app = FastAPI(
    title="AI Agent MCP Server",
    description="Model Context Protocol server for AI agent tools",
    version="0.1.0",
)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint - health check."""
    return {"status": "ok", "message": "AI Agent MCP Server is running"}

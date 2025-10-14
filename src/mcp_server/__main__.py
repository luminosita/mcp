"""
Entry point for module execution (python -m mcp_server).

Enables running the application using: python -m mcp_server
"""

from mcp_server.main import app

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)  # noqa: S104

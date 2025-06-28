"""API endpoints for the MCP server.

This module contains the FastAPI route definitions for the MCP server's API endpoints.
"""

from fastapi import APIRouter

from . import comby, semgrep

# Create a router for the API endpoints
router = APIRouter(prefix="/api/v1", tags=["mcp"])

router.include_router(comby.router, prefix="/comby", tags=["comby"])
router.include_router(semgrep.router, prefix="/semgrep", tags=["semgrep"])

"""API endpoints for the MCP server.

This module contains the FastAPI route definitions for the MCP server's API endpoints.
"""

from fastapi import APIRouter

# Create a router for the API endpoints
router = APIRouter(prefix="/api/v1", tags=["mcp"])

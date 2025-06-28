"""Main application module for the MCP server.

This module contains the FastAPI application and serves as the entry point for the service.
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from mcp_server.api import router as api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Semantic Fabric MCP Server",
    description="Model Context Protocol server for structural code search and replace operations",
    version="0.1.0",
    contact={
        "name": "Semantic Fabric Team",
    },
    license_info={
        "name": "MIT",
    },
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers

app.include_router(api_router)


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint for load balancers and monitoring."""
    return {"status": "ok"}


@app.on_event("startup")
async def startup_event():
    """Initialize application services on startup."""
    logger.info("Starting MCP Server")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up application resources on shutdown."""
    logger.info("Shutting down MCP Server")

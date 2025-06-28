"""Service layer for the MCP server.

This module contains the business logic and service implementations for the MCP server,
including the Comby runner and other core services.
"""

# Import services to make them available when importing from the services package
from .comby_runner import CombyRunner  # noqa: F401

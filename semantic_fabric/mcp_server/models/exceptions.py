"""Custom exceptions for the MCP server."""


class McpServerError(Exception):
    """Base exception for MCP Server errors."""

    pass


class CombyError(McpServerError):
    """Exception raised for errors during Comby operations."""

    pass

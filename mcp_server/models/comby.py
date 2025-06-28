"""Pydantic models for Comby operations.

This module defines the data structures for requests and responses for the
Comby-related API endpoints.
"""

from pydantic import BaseModel, Field


class CombyScanRequest(BaseModel):
    """Request model for a Comby scan operation."""

    match_template: str = Field(..., description="The Comby match template.")
    rewrite_template: str = Field(..., description="The Comby rewrite template.")
    file_filters: list[str] | None = Field(None, description="A list of file extensions to include in the scan.")


class CombyIdeateRequest(BaseModel):
    """Request model for a Comby ideate operation."""

    code_snippet: str = Field(..., description="The code snippet to transform.")
    match_template: str = Field(..., description="The Comby match template.")
    rewrite_template: str = Field(..., description="The Comby rewrite template.")


class CombyExecuteRequest(BaseModel):
    """Request model for a Comby execute operation."""

    match_template: str = Field(..., description="The Comby match template.")
    rewrite_template: str = Field(..., description="The Comby rewrite template.")
    file_filters: list[str] | None = Field(None, description="A list of file extensions to include in the scan.")


class CombyMatch(BaseModel):
    """Represents a single match found by Comby."""

    uri: str = Field(..., description="The file path of the match.")
    matched: str = Field(..., description="The code that was matched.")


class CombyScanResponse(BaseModel):
    """Response model for a Comby scan operation."""

    matches: list[CombyMatch] = Field(..., description="A list of matches found.")


class CombyIdeateResponse(BaseModel):
    """Response model for a Comby ideate operation."""

    transformed_code: str = Field(..., description="The transformed code snippet.")


class CombyExecuteResponse(BaseModel):
    """Response model for a Comby execute operation."""

    success: bool = Field(..., description="Whether the operation was successful.")
    files_changed: int = Field(..., description="The number of files changed.")

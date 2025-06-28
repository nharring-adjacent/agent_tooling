"""Pydantic models for Semgrep operations.

This module defines the data structures for requests and responses for the
Semgrep-related API endpoints.
"""

from pydantic import BaseModel, Field


class SemgrepScanRequest(BaseModel):
    """Request model for a Semgrep scan operation."""

    pattern: str = Field(..., description="The Semgrep pattern to scan for.")
    file_filters: list[str] | None = Field(None, description="A list of file extensions to include in the scan.")


class SemgrepIdeateRequest(BaseModel):
    """Request model for a Semgrep ideate operation (scan on a snippet)."""

    code_snippet: str = Field(..., description="The code snippet to scan.")
    pattern: str = Field(..., description="The Semgrep pattern to scan for.")


class SemgrepExecuteRequest(BaseModel):
    """Request model for a Semgrep execute operation (apply rules)."""

    rules: str = Field(..., description="The Semgrep rules in YAML format.")
    file_filters: list[str] | None = Field(None, description="A list of file extensions to include in the execution.")


class SemgrepMatch(BaseModel):
    """Represents a single match found by Semgrep."""

    uri: str = Field(..., description="The file path of the match.")
    start: dict = Field(..., description="The start position of the match.")
    end: dict = Field(..., description="The end position of the match.")
    text: str = Field(..., description="The matched text.")
    extra: dict = Field(..., description="Additional information about the match.")


class SemgrepScanResponse(BaseModel):
    """Response model for a Semgrep scan operation."""

    matches: list[SemgrepMatch] = Field(..., description="A list of matches found.")


class SemgrepIdeateResponse(BaseModel):
    """Response model for a Semgrep ideate operation."""

    matches: list[SemgrepMatch] = Field(..., description="A list of matches found in the snippet.")


class SemgrepExecuteResponse(BaseModel):
    """Response model for a Semgrep execute operation."""

    matches: list[SemgrepMatch] = Field(..., description="A list of matches found.")

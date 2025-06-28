"""API endpoints for Semgrep operations."""

from fastapi import APIRouter, Depends

from mcp_server.models.semgrep import (
    SemgrepExecuteRequest,
    SemgrepExecuteResponse,
    SemgrepIdeateRequest,
    SemgrepIdeateResponse,
    SemgrepScanRequest,
    SemgrepScanResponse,
)
from mcp_server.services.semgrep import SemgrepService

router = APIRouter()


def get_semgrep_service():
    """Dependency injector for the SemgrepService."""
    return SemgrepService()


@router.post("/scan", response_model=SemgrepScanResponse)
async def scan(request: SemgrepScanRequest, service: SemgrepService = Depends(get_semgrep_service)):
    """Perform a Semgrep scan operation."""
    return service.scan(request)


@router.post("/ideate", response_model=SemgrepIdeateResponse)
async def ideate(request: SemgrepIdeateRequest, service: SemgrepService = Depends(get_semgrep_service)):
    """Perform a Semgrep scan on a code snippet."""
    return service.ideate(request)


@router.post("/execute", response_model=SemgrepExecuteResponse)
async def execute(request: SemgrepExecuteRequest, service: SemgrepService = Depends(get_semgrep_service)):
    """Execute a Semgrep rule against files."""
    return service.execute(request)

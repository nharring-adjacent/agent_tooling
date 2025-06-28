"""API endpoints for Comby operations."""

from fastapi import APIRouter, Depends

from mcp_server.models.comby import (
    CombyExecuteRequest,
    CombyExecuteResponse,
    CombyIdeateRequest,
    CombyIdeateResponse,
    CombyScanRequest,
    CombyScanResponse,
)
from mcp_server.services.comby import CombyService

router = APIRouter()


def get_comby_service():
    """Dependency injector for the CombyService."""
    return CombyService()


@router.post("/scan", response_model=CombyScanResponse)
async def scan(request: CombyScanRequest, service: CombyService = Depends(get_comby_service)):
    """Perform a dry-run structural code search."""
    return service.scan(request)


@router.post("/ideate", response_model=CombyIdeateResponse)
async def ideate(request: CombyIdeateRequest, service: CombyService = Depends(get_comby_service)):
    """Transform a code snippet without side effects."""
    return service.ideate(request)


@router.post("/execute", response_model=CombyExecuteResponse)
async def execute(request: CombyExecuteRequest, service: CombyService = Depends(get_comby_service)):
    """Execute a structural code transformation across the project."""
    return service.execute(request)

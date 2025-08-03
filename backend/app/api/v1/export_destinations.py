"""
Export Destinations API endpoints
"""

import logging
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.v1.deps import get_export_destination_service
from app.schemas.export_destination import (
    ConnectionTestResponse,
    DestinationAuthFieldsResponse,
    ExportDestinationCreate,
    ExportDestinationResponse,
    ExportDestinationTypesResponse,
    ExportDestinationUpdate,
    ExportRequest,
    ExportRunResponse,
)
from app.services.export_destination_service import ExportDestinationService
from export_pipeline.orchestrator import ExportOrchestrator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/export-destinations", tags=["export-destinations"])


@router.post("/", response_model=ExportDestinationResponse)
async def create_export_destination(
    destination_data: ExportDestinationCreate,
    service: ExportDestinationService = Depends(get_export_destination_service),
):
    """Create a new export destination."""

    # Validate configuration
    validation = service.validate_destination_config(
        destination_data.destination_type,
        {
            "auth_config": destination_data.auth_config,
            "destination_config": destination_data.destination_config,
        },
    )

    if not validation["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid configuration: {', '.join(validation['errors'])}",
        )

    try:
        destination = service.create_destination(destination_data.model_dump())
        return ExportDestinationResponse.model_validate(destination.to_dict())
    except Exception as e:
        logger.error(f"Failed to create export destination: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create export destination",
        ) from e


@router.get("/", response_model=list[ExportDestinationResponse])
async def list_export_destinations(
    destination_type: str | None = None,
    is_active: bool | None = None,
    service: ExportDestinationService = Depends(get_export_destination_service),
):
    """List export destinations."""
    destinations = service.list_destinations(destination_type, is_active)
    return [
        ExportDestinationResponse.model_validate(dest.to_dict())
        for dest in destinations
    ]


@router.get("/{destination_id}", response_model=ExportDestinationResponse)
async def get_export_destination(
    destination_id: UUID,
    service: ExportDestinationService = Depends(get_export_destination_service),
):
    """Get export destination by ID."""
    destination = service.get_destination(destination_id)

    if not destination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Export destination not found"
        )

    return ExportDestinationResponse.model_validate(destination.to_dict())


@router.put("/{destination_id}", response_model=ExportDestinationResponse)
async def update_export_destination(
    destination_id: UUID,
    update_data: ExportDestinationUpdate,
    service: ExportDestinationService = Depends(get_export_destination_service),
):
    """Update export destination."""

    # Get existing destination to validate type
    existing = service.get_destination(destination_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Export destination not found"
        )

    # Validate configuration if provided
    update_dict = update_data.model_dump(exclude_unset=True)
    if "auth_config" in update_dict or "destination_config" in update_dict:
        validation = service.validate_destination_config(
            existing.destination_type,
            {
                "auth_config": update_dict.get("auth_config", existing.auth_config),
                "destination_config": update_dict.get(
                    "destination_config", existing.destination_config
                ),
            },
        )

        if not validation["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid configuration: {', '.join(validation['errors'])}",
            )

    try:
        destination = service.update_destination(destination_id, update_dict)
        if not destination:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Export destination not found",
            )

        return ExportDestinationResponse.model_validate(destination.to_dict())
    except Exception as e:
        logger.error(f"Failed to update export destination: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update export destination",
        ) from e


@router.delete("/{destination_id}")
async def delete_export_destination(
    destination_id: UUID,
    service: ExportDestinationService = Depends(get_export_destination_service),
):
    """Delete export destination."""

    if not service.delete_destination(destination_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Export destination not found"
        )

    return {"message": "Export destination deleted successfully"}


@router.post("/{destination_id}/test", response_model=ConnectionTestResponse)
async def test_destination_connection(
    destination_id: UUID,
    service: ExportDestinationService = Depends(get_export_destination_service),
):
    """Test connection to export destination."""
    result = service.test_destination_connection(destination_id)
    return ConnectionTestResponse(**result)


@router.post("/{destination_id}/export", response_model=dict[str, Any])
async def export_data(
    destination_id: UUID,
    export_request: ExportRequest,
    service: ExportDestinationService = Depends(get_export_destination_service),
):
    """Export data to destination."""

    # Verify destination exists
    destination = service.get_destination(destination_id)
    if not destination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Export destination not found"
        )

    if not destination.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Export destination is not active",
        )

    try:
        # Initialize export orchestrator
        orchestrator = ExportOrchestrator()

        # Start export without waiting for completion
        import asyncio

        asyncio.create_task(
            orchestrator.run_export(
                destination_id=destination_id,
                export_filters=export_request.filters,
                export_type=export_request.export_type,
            )
        )

        return {
            "message": "Export started successfully",
            "destination_id": str(destination_id),
        }

    except Exception as e:
        logger.error(f"Failed to start export for destination {destination_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start export: {str(e)}",
        ) from e


@router.get("/{destination_id}/runs", response_model=list[ExportRunResponse])
async def list_export_runs(
    destination_id: UUID,
    status: str | None = None,
    limit: int = 100,
    service: ExportDestinationService = Depends(get_export_destination_service),
):
    """List export runs for destination."""

    # Verify destination exists
    if not service.get_destination(destination_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Export destination not found"
        )

    runs = service.list_export_runs(destination_id, status, limit)
    return [ExportRunResponse.model_validate(run.to_dict()) for run in runs]


@router.get("/types/info")
def get_destination_types_info(
    service: ExportDestinationService = Depends(get_export_destination_service),
) -> ExportDestinationTypesResponse:
    """
    Get information about all supported export destination types.

    Returns details about available destination types, their authentication methods,
    and configuration options.
    """
    try:
        supported_types = service.get_supported_types()
        types_info = []

        for destination_type in supported_types:
            metadata = service.get_destination_metadata(destination_type)
            if metadata:
                types_info.append(metadata)

        return ExportDestinationTypesResponse(
            destination_types=types_info, count=len(types_info)
        )
    except Exception as e:
        logger.error(f"Error retrieving destination types information: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving destination types information: {str(e)}",
        ) from e


@router.get("/types/{destination_type}/auth-fields")
def get_auth_fields(
    destination_type: str,
    auth_method: str | None = Query(
        None, description="Specific auth method to get fields for"
    ),
    service: ExportDestinationService = Depends(get_export_destination_service),
) -> DestinationAuthFieldsResponse:
    """
    Get authentication field definitions for an export destination type.

    Returns the fields required for each supported authentication method.

    - **destination_type**: Type of destination (bigquery, snowflake, etc.)
    - **auth_method**: Optional specific auth method to get fields for
    """
    try:
        return service.get_auth_fields(destination_type, auth_method)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e

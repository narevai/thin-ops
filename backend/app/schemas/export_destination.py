"""
Export Destination Schemas
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class ExportDestinationBase(BaseModel):
    name: str = Field(..., description="Unique name for the export destination")
    destination_type: str = Field(
        ..., description="Type of destination (bigquery, snowflake, etc.)"
    )
    display_name: str | None = Field(None, description="Display name for UI")
    is_active: bool = Field(True, description="Whether destination is active")


class ExportDestinationCreate(ExportDestinationBase):
    auth_config: dict[str, Any] = Field(..., description="Authentication configuration")
    destination_config: dict[str, Any] = Field(
        default_factory=dict, description="Destination-specific configuration"
    )


class ExportDestinationUpdate(BaseModel):
    name: str | None = None
    display_name: str | None = None
    is_active: bool | None = None
    auth_config: dict[str, Any] | None = None
    destination_config: dict[str, Any] | None = None


class ExportDestinationResponse(ExportDestinationBase):
    id: UUID
    is_validated: bool
    last_validation_at: datetime | None = None
    last_export_at: datetime | None = None
    last_export_status: str | None = None
    export_statistics: dict[str, Any] | None = None
    auth_configured: bool
    auth_method: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConnectionTestResponse(BaseModel):
    success: bool
    message: str
    details: dict[str, Any] | None = None
    error: str | None = None


class ExportFilters(BaseModel):
    start_date: datetime | None = None
    end_date: datetime | None = None
    provider_id: UUID | None = None
    service_category: str | None = None
    service_name: str | None = None
    min_cost: float | None = None
    max_cost: float | None = None


class ExportRequest(BaseModel):
    export_type: str = Field(
        default="filtered", description="Type of export (full, incremental, filtered)"
    )
    filters: dict[str, Any] = Field(default_factory=dict, description="Export filters")


class ExportRunResponse(BaseModel):
    id: UUID
    destination_id: UUID
    export_type: str
    status: str
    start_date: datetime | None = None
    end_date: datetime | None = None
    filters: dict[str, Any] | None = None
    records_exported: str | None = None
    records_failed: str | None = None
    export_size_bytes: str | None = None
    started_at: datetime
    completed_at: datetime | None = None
    duration_seconds: str | None = None
    error_message: str | None = None
    dlt_pipeline_name: str | None = None
    dlt_load_id: str | None = None

    class Config:
        from_attributes = True


class ExportDestinationTypesResponse(BaseModel):
    """Response schema for export destination types info."""

    destination_types: list[dict[str, Any]]
    count: int

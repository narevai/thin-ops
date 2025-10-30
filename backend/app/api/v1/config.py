"""
NarevAI Billing Analyzer - Config API v1
"""

from fastapi import APIRouter
from pydantic import BaseModel

from app.config import get_settings

router = APIRouter(prefix="/config", tags=["config"])


class ConfigResponse(BaseModel):
    """Configuration response schema."""
    
    settings: "SettingsResponse"


class SettingsResponse(BaseModel):
    """Settings response schema."""
    
    demo: bool


@router.get("", response_model=ConfigResponse)
def get_config() -> ConfigResponse:
    """
    Get application configuration.

    Returns basic configuration information including demo mode status.
    """
    settings = get_settings()

    return ConfigResponse(settings=SettingsResponse(demo=settings.demo))

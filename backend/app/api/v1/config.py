from fastapi import APIRouter

from app.config import get_settings
from app.schemas.config import ConfigResponse, SettingsResponse

router = APIRouter(prefix="/config", tags=["config"])


@router.get("", response_model=ConfigResponse)
def get_config() -> ConfigResponse:
    """
    Get application configuration.

    Returns basic configuration information including demo mode status.
    """
    settings = get_settings()

    return ConfigResponse(settings=SettingsResponse(demo=settings.demo))

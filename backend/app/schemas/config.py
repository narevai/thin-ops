"""
Config API Schemas
"""

from pydantic import BaseModel


class SettingsResponse(BaseModel):
    """Settings response schema."""

    demo: bool


class ConfigResponse(BaseModel):
    """Configuration response schema."""

    settings: SettingsResponse

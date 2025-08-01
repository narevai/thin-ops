"""
Shared authentication schemas
"""

from pydantic import BaseModel


class AuthFieldConfig(BaseModel):
    """Configuration for a single auth field."""

    required: bool = True
    type: str = "string"  # string, number, boolean, etc.
    placeholder: str | None = None
    description: str | None = None
    fields: dict[str, "AuthFieldConfig"] | None = None


class AuthFieldsResponse(BaseModel):
    """Response schema for auth fields - generic for providers and destinations."""

    type: str  # provider_type or destination_type
    supported_auth_methods: list[str]
    default_auth_method: str
    auth_fields: dict[str, dict[str, AuthFieldConfig]]


class ProviderAuthFieldsResponse(AuthFieldsResponse):
    """Response schema for provider auth fields."""

    @property
    def provider_type(self) -> str:
        return self.type


class DestinationAuthFieldsResponse(AuthFieldsResponse):
    """Response schema for destination auth fields."""

    @property
    def destination_type(self) -> str:
        return self.type

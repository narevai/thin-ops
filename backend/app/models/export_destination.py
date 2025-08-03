"""
Export Destination Model
"""

from typing import Any
from uuid import uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.config import get_settings
from app.database import Base

settings = get_settings()


def get_json_field():
    """Get appropriate JSON field type based on database."""
    return JSONB if settings.is_postgres else JSON


class ExportDestination(Base):
    """Export destination configuration table with flexible authentication support."""

    __tablename__ = "export_destinations"

    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))

    # Destination identification
    name = Column(String(100), nullable=False, unique=True)
    destination_type = Column(
        String(50), nullable=False
    )  # 'bigquery', 'snowflake', 'redshift', 's3'
    display_name = Column(String(200))

    # Authentication
    auth_config = Column(get_json_field())

    # Configuration
    destination_config = Column(get_json_field())

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_validated = Column(Boolean, default=False)
    last_validation_at = Column(DateTime(timezone=True))
    validation_error = Column(Text)

    # Export metadata
    last_export_at = Column(DateTime(timezone=True))
    last_export_status = Column(String(50))  # 'success', 'failed', 'partial'
    last_export_error = Column(Text)
    export_statistics = Column(get_json_field())

    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    created_by = Column(String(255))
    updated_by = Column(String(255))

    # Relationships
    export_runs = relationship(
        "ExportRun", back_populates="destination", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<ExportDestination(id={self.id}, name={self.name}, type={self.destination_type}, active={self.is_active})>"

    def get_auth_config(self) -> dict[str, Any] | None:
        """Get authentication configuration."""
        return self.auth_config

    def set_auth_config(self, auth_config: dict[str, Any]) -> None:
        """Set authentication configuration."""
        self.auth_config = auth_config

    def to_dict(self, include_sensitive=False):
        """Convert to dictionary for API responses."""
        data = {
            "id": self.id,
            "name": self.name,
            "destination_type": self.destination_type,
            "display_name": self.display_name,
            "is_active": self.is_active,
            "is_validated": self.is_validated,
            "last_validation_at": self.last_validation_at.isoformat()
            if self.last_validation_at
            else None,
            "last_export_at": self.last_export_at.isoformat()
            if self.last_export_at
            else None,
            "last_export_status": self.last_export_status,
            "export_statistics": self.export_statistics,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_sensitive:
            data["destination_config"] = self.destination_config

        # Include auth status (non-sensitive)
        if self.auth_config:
            data["auth_configured"] = True
            # Try to get method from encrypted auth_config
            try:
                from app.services.encryption_service import EncryptionService

                encryption_service = EncryptionService()
                decrypted_auth = encryption_service.decrypt_dict(self.auth_config)
                data["auth_method"] = decrypted_auth.get("method", "unknown")
            except Exception:
                data["auth_method"] = "unknown"
        else:
            data["auth_configured"] = False
            data["auth_method"] = None

        return data

"""
Export Destination Service
"""

import logging
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.export_destination import ExportDestination
from app.models.export_run import ExportRun
from app.services.encryption_service import EncryptionService
from export_destinations.registry import ExportDestinationRegistry

logger = logging.getLogger(__name__)


class ExportDestinationService:
    """Service for managing export destinations."""

    def __init__(self, db: Session):
        self.db = db
        self.encryption_service = EncryptionService()

    def create_destination(self, destination_data: dict[str, Any]) -> ExportDestination:
        """Create a new export destination."""
        # Encrypt auth config
        auth_config = destination_data.get("auth_config", {})
        if auth_config:
            encrypted_auth = self.encryption_service.encrypt_dict(auth_config)
            destination_data["auth_config"] = encrypted_auth

        destination = ExportDestination(**destination_data)
        self.db.add(destination)
        self.db.commit()
        self.db.refresh(destination)

        logger.info(f"Created export destination: {destination.name}")
        return destination

    def get_destination(self, destination_id: UUID) -> ExportDestination | None:
        """Get export destination by ID."""
        return (
            self.db.query(ExportDestination)
            .filter(ExportDestination.id == str(destination_id))
            .first()
        )

    def list_destinations(
        self, destination_type: str | None = None, is_active: bool | None = None
    ) -> list[ExportDestination]:
        """List export destinations with optional filters."""
        query = self.db.query(ExportDestination)

        if destination_type:
            query = query.filter(ExportDestination.destination_type == destination_type)
        if is_active is not None:
            query = query.filter(ExportDestination.is_active == is_active)

        return query.all()

    def update_destination(
        self, destination_id: UUID, update_data: dict[str, Any]
    ) -> ExportDestination | None:
        """Update export destination."""
        destination = self.get_destination(destination_id)
        if not destination:
            return None

        # Encrypt auth config if provided
        if "auth_config" in update_data:
            auth_config = update_data["auth_config"]
            if auth_config:
                encrypted_auth = self.encryption_service.encrypt_dict(auth_config)
                update_data["auth_config"] = encrypted_auth

        for key, value in update_data.items():
            if hasattr(destination, key):
                setattr(destination, key, value)

        self.db.commit()
        self.db.refresh(destination)

        logger.info(f"Updated export destination: {destination.name}")
        return destination

    def delete_destination(self, destination_id: UUID) -> bool:
        """Delete export destination."""
        destination = self.get_destination(destination_id)
        if not destination:
            return False

        self.db.delete(destination)
        self.db.commit()

        logger.info(f"Deleted export destination: {destination.name}")
        return True

    def test_destination_connection(self, destination_id: UUID) -> dict[str, Any]:
        """Test connection to export destination."""
        destination = self.get_destination(destination_id)
        if not destination:
            return {
                "success": False,
                "message": "Export destination not found",
            }

        try:
            # Get destination config with decrypted auth
            config = self.get_destination_config(destination_id)
            if not config:
                return {
                    "success": False,
                    "message": "Failed to get destination configuration",
                }

            # Create destination instance and test
            dest_instance = ExportDestinationRegistry.create_destination(
                destination.destination_type, config
            )
            if not dest_instance:
                return {
                    "success": False,
                    "message": f"Unsupported destination type: {destination.destination_type}",
                }

            result = dest_instance.test_connection()

            # Update validation status
            destination.is_validated = result["success"]
            destination.last_validation_at = (
                self.encryption_service._get_encryption_key()
            )  # Use current time
            if not result["success"]:
                destination.validation_error = result.get(
                    "message", "Connection test failed"
                )
            else:
                destination.validation_error = None

            self.db.commit()

            return result

        except Exception as e:
            logger.error(
                f"Connection test failed for destination {destination_id}: {e}"
            )
            return {
                "success": False,
                "message": f"Connection test error: {str(e)}",
            }

    def get_destination_config(self, destination_id: UUID) -> dict[str, Any] | None:
        """Get destination configuration with decrypted auth."""
        destination = self.get_destination(destination_id)
        if not destination:
            return None

        config = {
            "id": destination.id,
            "name": destination.name,
            "destination_type": destination.destination_type,
            "display_name": destination.display_name,
            "destination_config": destination.destination_config or {},
        }

        # Decrypt auth config
        if destination.auth_config:
            try:
                decrypted_auth = self.encryption_service.decrypt_dict(
                    destination.auth_config
                )
                config["auth_config"] = decrypted_auth
            except Exception as e:
                logger.error(
                    f"Failed to decrypt auth config for destination {destination_id}: {e}"
                )
                return None

        return config

    def validate_destination_config(
        self, destination_type: str, config: dict[str, Any]
    ) -> dict[str, Any]:
        """Validate destination configuration."""
        return ExportDestinationRegistry.validate_config(destination_type, config)

    def get_supported_types(self) -> list[str]:
        """Get supported destination types."""
        return ExportDestinationRegistry.get_supported_types()

    def get_destination_metadata(self, destination_type: str) -> dict[str, Any] | None:
        """Get metadata for a destination type."""
        return ExportDestinationRegistry.get_destination_metadata(destination_type)

    # Export run methods
    def create_export_run(self, run_data: dict[str, Any]) -> ExportRun:
        """Create a new export run."""
        export_run = ExportRun(**run_data)
        self.db.add(export_run)
        self.db.commit()
        self.db.refresh(export_run)
        return export_run

    def get_export_run(self, run_id: UUID) -> ExportRun | None:
        """Get export run by ID."""
        return self.db.query(ExportRun).filter(ExportRun.id == str(run_id)).first()

    def list_export_runs(
        self,
        destination_id: UUID | None = None,
        status: str | None = None,
        limit: int = 100,
    ) -> list[ExportRun]:
        """List export runs with optional filters."""
        query = self.db.query(ExportRun)

        if destination_id:
            query = query.filter(ExportRun.destination_id == str(destination_id))
        if status:
            query = query.filter(ExportRun.status == status)

        return query.order_by(ExportRun.started_at.desc()).limit(limit).all()

    def update_export_run(
        self, run_id: UUID, update_data: dict[str, Any]
    ) -> ExportRun | None:
        """Update export run."""
        export_run = self.get_export_run(run_id)
        if not export_run:
            return None

        for key, value in update_data.items():
            if hasattr(export_run, key):
                setattr(export_run, key, value)

        self.db.commit()
        self.db.refresh(export_run)
        return export_run

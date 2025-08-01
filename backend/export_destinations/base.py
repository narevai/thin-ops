"""
Base Export Destination Class
"""

import logging
from abc import ABC, abstractmethod
from typing import Any

import dlt

logger = logging.getLogger(__name__)


class BaseExportDestination(ABC):
    """Base class for all export destinations."""

    def __init__(self, config: dict[str, Any]):
        """
        Initialize base export destination.

        Args:
            config: Destination configuration containing:
                - destination_type: Type of destination
                - auth_config: Authentication configuration
                - destination_config: Destination-specific config
        """
        self.config = config
        self.destination_type = config.get("destination_type", "")
        self.auth_config = config.get("auth_config", {})
        self.destination_config = config.get("destination_config", {})

    @abstractmethod
    def get_dlt_destination(self):
        """
        Get DLT destination instance.

        Returns:
            Configured DLT destination
        """
        pass

    @abstractmethod
    def get_dlt_credentials(self) -> dict[str, Any]:
        """
        Get DLT credentials configuration.

        Returns:
            Credentials dictionary for DLT
        """
        pass

    @abstractmethod
    def test_connection(self) -> dict[str, Any]:
        """
        Test connection to the destination.

        Returns:
            Dictionary with:
                - success: bool
                - message: str
                - details: dict (optional)
        """
        pass

    @abstractmethod
    def transform_for_destination(
        self, records: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Transform records for destination-specific requirements.

        Args:
            records: List of billing records

        Returns:
            Transformed records
        """
        pass

    def prepare_dlt_pipeline(
        self, pipeline_name: str, dataset_name: str
    ) -> dlt.Pipeline:
        """
        Prepare DLT pipeline for this destination.

        Args:
            pipeline_name: Name of the DLT pipeline
            dataset_name: Dataset/schema name

        Returns:
            Configured DLT pipeline
        """
        return dlt.pipeline(
            pipeline_name=pipeline_name,
            destination=self.get_dlt_destination(),
            dataset_name=dataset_name,
        )

    def get_export_schema(self) -> dict[str, Any]:
        """
        Get schema configuration for export.

        Returns:
            Schema configuration dict
        """
        return {
            "write_disposition": self.destination_config.get(
                "write_disposition", "append"
            ),
            "primary_key": self.destination_config.get("primary_key", ["id"]),
            "merge_key": self.destination_config.get("merge_key"),
        }

    def validate_config(self) -> dict[str, Any]:
        """
        Validate destination configuration.

        Returns:
            Validation result dict
        """
        errors = []

        # Check required auth fields
        required_auth = self.get_required_auth_fields()
        for field in required_auth:
            if field not in self.auth_config or not self.auth_config[field]:
                errors.append(f"Missing required auth field: {field}")

        # Check required config fields
        required_config = self.get_required_config_fields()
        for field in required_config:
            if (
                field not in self.destination_config
                or not self.destination_config[field]
            ):
                errors.append(f"Missing required config field: {field}")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
        }

    def get_required_auth_fields(self) -> list[str]:
        """
        Get list of required authentication fields.

        Returns:
            List of required field names
        """
        return []

    def get_required_config_fields(self) -> list[str]:
        """
        Get list of required configuration fields.

        Returns:
            List of required field names
        """
        return []

    def get_default_config(self) -> dict[str, Any]:
        """
        Get default configuration values.

        Returns:
            Default configuration dict
        """
        return {
            "write_disposition": "append",
            "batch_size": 1000,
            "timeout_seconds": 300,
        }

    def __repr__(self) -> str:
        """String representation of destination."""
        return f"{self.__class__.__name__}(type={self.destination_type})"

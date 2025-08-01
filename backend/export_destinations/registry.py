"""
Export Destination Registry
"""

import importlib
import logging
from pathlib import Path
from typing import Any

from export_destinations.base import BaseExportDestination

logger = logging.getLogger(__name__)


class ExportDestinationRegistry:
    """Registry for export destinations."""

    _destinations: dict[str, dict[str, Any]] = {}

    @classmethod
    def register(
        cls,
        destination_type: str,
        display_name: str,
        description: str = "",
        supported_features: list[str] | None = None,
        supported_auth_methods: list[str] | None = None,
        default_auth_method: str | None = None,
        required_auth_fields: list[str] | None = None,
        auth_fields: dict[str, Any] | None = None,
        required_config_fields: list[str] | None = None,
        optional_config_fields: list[str] | None = None,
        version: str = "1.0.0",
        default_config: dict[str, Any] | None = None,
        field_descriptions: dict[str, str] | None = None,
        field_types: dict[str, str] | None = None,
    ):
        """
        Register an export destination.

        Args:
            destination_type: Unique identifier for the destination
            display_name: Human-readable name
            description: Destination description
            supported_features: List of supported features
            supported_auth_methods: List of supported authentication methods
            default_auth_method: Default authentication method
            required_auth_fields: Required authentication fields
            auth_fields: Authentication field definitions for UI
            required_config_fields: Required configuration fields
            optional_config_fields: Optional configuration fields
            version: Destination version
            default_config: Default configuration values
            field_descriptions: Field descriptions
            field_types: Field types
        """

        def decorator(
            destination_class: type[BaseExportDestination],
        ) -> type[BaseExportDestination]:
            if not issubclass(destination_class, BaseExportDestination):
                raise TypeError(
                    f"{destination_class} must inherit from BaseExportDestination"
                )

            cls._destinations[destination_type] = {
                "class": destination_class,
                "metadata": {
                    "destination_type": destination_type,
                    "display_name": display_name,
                    "description": description,
                    "supported_features": supported_features or [],
                    "supported_auth_methods": supported_auth_methods or [],
                    "default_auth_method": default_auth_method,
                    "required_auth_fields": required_auth_fields or [],
                    "auth_fields": auth_fields or {},
                    "required_config_fields": required_config_fields or [],
                    "optional_config_fields": optional_config_fields or [],
                    "version": version,
                    "default_config": default_config or {},
                    "field_descriptions": field_descriptions or {},
                    "field_types": field_types or {},
                },
            }

            logger.info(f"Registered export destination: {destination_type}")
            return destination_class

        return decorator

    @classmethod
    def get_destination_class(
        cls, destination_type: str
    ) -> type[BaseExportDestination] | None:
        """Get destination class by type."""
        if destination_type not in cls._destinations:
            cls._load_destination(destination_type)

        destination_info = cls._destinations.get(destination_type)
        return destination_info["class"] if destination_info else None

    @classmethod
    def create_destination(
        cls, destination_type: str, config: dict[str, Any]
    ) -> BaseExportDestination | None:
        """Create destination instance."""
        destination_class = cls.get_destination_class(destination_type)
        if not destination_class:
            logger.error(f"Destination type not found: {destination_type}")
            return None

        config["destination_type"] = destination_type
        return destination_class(config)

    @classmethod
    def get_destination_metadata(cls, destination_type: str) -> dict[str, Any] | None:
        """Get destination metadata."""
        if destination_type not in cls._destinations:
            cls._load_destination(destination_type)

        destination_info = cls._destinations.get(destination_type)
        return destination_info["metadata"] if destination_info else None

    @classmethod
    def get_supported_types(cls) -> list[str]:
        """Get list of all supported destination types."""
        registered = set(cls._destinations.keys())
        available = set(cls._discover_available_destinations())
        return sorted(registered | available)

    @classmethod
    def validate_config(
        cls, destination_type: str, config: dict[str, Any]
    ) -> dict[str, Any]:
        """Validate destination configuration."""
        metadata = cls.get_destination_metadata(destination_type)
        if not metadata:
            return {
                "valid": False,
                "errors": [f"Unknown destination type: {destination_type}"],
            }

        errors = []

        # Check required auth fields
        for field in metadata["required_auth_fields"]:
            auth_config = config.get("auth_config", {})
            if field not in auth_config or not auth_config[field]:
                errors.append(f"Missing required auth field: {field}")

        # Check required config fields
        for field in metadata["required_config_fields"]:
            dest_config = config.get("destination_config", {})
            if field not in dest_config or not dest_config[field]:
                errors.append(f"Missing required config field: {field}")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
        }

    @classmethod
    def _discover_available_destinations(cls) -> list[str]:
        """Discover available destination packages."""
        try:
            import export_destinations

            destinations_path = Path(export_destinations.__file__).parent

            available = []
            for item in destinations_path.iterdir():
                if item.is_dir() and not item.name.startswith("_"):
                    if (item / "destination.py").exists():
                        available.append(item.name)

            return available
        except Exception as e:
            logger.error(f"Error discovering destinations: {e}")
            return []

    @classmethod
    def _load_destination(cls, destination_type: str) -> bool:
        """Load a specific destination module."""
        if destination_type in cls._destinations:
            return True

        try:
            module_name = f"export_destinations.{destination_type}.destination"
            importlib.import_module(module_name)
            logger.debug(f"Loaded destination: {destination_type}")
            return True
        except ImportError as e:
            logger.warning(f"Failed to load destination {destination_type}: {e}")
            return False

    @classmethod
    def clear(cls):
        """Clear registry (for testing)."""
        cls._destinations.clear()


# Convenience functions
def get_destination(
    destination_type: str, config: dict[str, Any]
) -> BaseExportDestination | None:
    """Create a configured destination instance."""
    return ExportDestinationRegistry.create_destination(destination_type, config)

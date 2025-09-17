"""
BigQuery Export Destination
"""

import logging
from typing import Any

import dlt

from export_destinations.base import BaseExportDestination
from export_destinations.bigquery.auth import BigQueryAuth
from export_destinations.registry import ExportDestinationRegistry

logger = logging.getLogger(__name__)


@ExportDestinationRegistry.register(
    destination_type="bigquery",
    display_name="Google BigQuery",
    description="Export data to Google BigQuery data warehouse",
    supported_features=["incremental_loading", "schema_evolution", "partitioning"],
    # Auth metadata from auth module
    supported_auth_methods=BigQueryAuth.SUPPORTED_METHODS,
    default_auth_method=BigQueryAuth.DEFAULT_METHOD,
    auth_fields=BigQueryAuth.AUTH_FIELDS,
    required_config_fields=["project_id", "dataset_id"],
    optional_config_fields=[
        "table_name",
        "write_disposition",
        "partition_field",
        "cluster_fields",
        "location",
    ],
    default_config={
        "write_disposition": "merge",
        "location": "US",
        "table_name": "billing_data_export",
        "batch_size": 1000,
    },
    # Field descriptions
    field_descriptions={
        "project_id": "Google Cloud Project ID",
        "dataset_id": "BigQuery dataset name",
        "table_name": "Target table name",
        "write_disposition": "How to handle existing data (append, replace, merge)",
        "partition_field": "Field to use for table partitioning",
        "cluster_fields": "Fields to use for table clustering",
        "location": "BigQuery dataset location",
    },
    field_types={
        "project_id": "string",
        "dataset_id": "string",
        "table_name": "string",
        "write_disposition": "select",
        "partition_field": "string",
        "cluster_fields": "array",
        "location": "string",
    },
)
class BigQueryDestination(BaseExportDestination):
    """BigQuery export destination implementation."""

    def get_dlt_destination(self):
        """Get DLT BigQuery destination."""
        credentials = self.get_dlt_credentials()
        location = self.destination_config.get("location", "US")

        return dlt.destinations.bigquery(
            credentials=credentials.get("credentials"),
            location=location,
        )

    def get_dlt_credentials(self) -> dict[str, Any]:
        """Get DLT credentials for BigQuery."""
        return BigQueryAuth.get_credentials_from_config(self.auth_config)

    def test_connection(self) -> dict[str, Any]:
        """Test BigQuery connection."""
        project_id = self.destination_config.get("project_id")
        return BigQueryAuth.test_connection(self.auth_config, project_id)

    def transform_for_destination(
        self, records: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Transform records for BigQuery.

        Args:
            records: List of billing records

        Returns:
            Transformed records
        """
        transformed = []

        for record in records:
            # Create a copy to avoid modifying original
            transformed_record = record.copy()

            # Convert any Decimal types to float for BigQuery compatibility
            for key, value in transformed_record.items():
                if hasattr(value, "to_decimal"):  # Handle Decimal types
                    transformed_record[key] = float(value)
                elif isinstance(value, dict):
                    # Handle nested objects - convert to JSON string if needed
                    continue  # BigQuery supports nested objects
                elif value is None:
                    # Keep None values as-is
                    continue

            transformed.append(transformed_record)

        return transformed

    def get_required_auth_fields(self) -> list[str]:
        """Get required authentication fields."""
        return ["method"]

    def get_required_config_fields(self) -> list[str]:
        """Get required configuration fields."""
        return ["project_id", "dataset_id"]

    def get_export_schema(self) -> dict[str, Any]:
        """Get export schema configuration."""
        schema = super().get_export_schema()

        # BigQuery-specific schema options
        schema.update(
            {
                "table_name": self.destination_config.get(
                    "table_name", "billing_data_export"
                ),
                "partition": self._get_partition_config(),
                "cluster": self._get_cluster_config(),
            }
        )

        return schema

    def _get_partition_config(self) -> dict[str, Any] | None:
        """Get partitioning configuration."""
        partition_field = self.destination_config.get("partition_field")
        if not partition_field:
            return None

        return {
            "field": partition_field,
            "data_type": "date",  # Assume date partitioning for billing data
            "granularity": "day",
        }

    def _get_cluster_config(self) -> list[str] | None:
        """Get clustering configuration."""
        cluster_fields = self.destination_config.get("cluster_fields")
        if isinstance(cluster_fields, str):
            return [cluster_fields]
        elif isinstance(cluster_fields, list):
            return cluster_fields
        return None

    def prepare_dlt_pipeline(
        self, pipeline_name: str, dataset_name: str
    ) -> dlt.Pipeline:
        """
        Prepare DLT pipeline for BigQuery.

        Args:
            pipeline_name: Name of the DLT pipeline
            dataset_name: Dataset name (will use configured dataset_id)

        Returns:
            Configured DLT pipeline
        """
        # Override dataset_name with configured dataset_id
        actual_dataset = self.destination_config.get("dataset_id", dataset_name)

        return dlt.pipeline(
            pipeline_name=pipeline_name,
            destination=self.get_dlt_destination(),
            dataset_name=actual_dataset,
        )

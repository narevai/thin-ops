"""
BigQuery Authentication
"""

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


class BigQueryAuth:
    """BigQuery authentication handler."""

    @staticmethod
    def get_credentials_from_config(auth_config: dict[str, Any]) -> dict[str, Any]:
        """
        Get BigQuery credentials from auth configuration.

        Args:
            auth_config: Authentication configuration

        Returns:
            Credentials dictionary for DLT BigQuery destination
        """
        auth_method = auth_config.get("method", "service_account")

        if auth_method == "service_account":
            return BigQueryAuth._get_service_account_credentials(auth_config)
        elif auth_method == "application_default":
            return BigQueryAuth._get_application_default_credentials()
        else:
            raise ValueError(f"Unsupported BigQuery auth method: {auth_method}")

    @staticmethod
    def _get_service_account_credentials(auth_config: dict[str, Any]) -> dict[str, Any]:
        """Get service account credentials."""
        credentials_json = auth_config.get("service_account_json")
        if not credentials_json:
            raise ValueError(
                "service_account_json is required for service_account auth"
            )

        # Parse JSON if it's a string
        if isinstance(credentials_json, str):
            try:
                credentials_dict = json.loads(credentials_json)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid service account JSON: {e}") from e
        else:
            credentials_dict = credentials_json

        # Validate required fields
        required_fields = [
            "type",
            "project_id",
            "private_key_id",
            "private_key",
            "client_email",
        ]
        missing_fields = [
            field for field in required_fields if field not in credentials_dict
        ]
        if missing_fields:
            raise ValueError(
                f"Missing required service account fields: {missing_fields}"
            )

        return {
            "credentials": credentials_dict,
            "project_id": credentials_dict.get("project_id"),
        }

    @staticmethod
    def _get_application_default_credentials() -> dict[str, Any]:
        """Get application default credentials."""
        return {
            "credentials": "default",
        }

    @staticmethod
    def validate_auth_config(auth_config: dict[str, Any]) -> dict[str, Any]:
        """
        Validate BigQuery authentication configuration.

        Args:
            auth_config: Authentication configuration

        Returns:
            Validation result
        """
        errors = []
        auth_method = auth_config.get("method")

        if not auth_method:
            errors.append("Authentication method is required")
        elif auth_method not in ["service_account", "application_default"]:
            errors.append(f"Unsupported auth method: {auth_method}")
        elif auth_method == "service_account":
            if not auth_config.get("service_account_json"):
                errors.append(
                    "service_account_json is required for service_account auth"
                )
            else:
                # Validate JSON structure
                try:
                    credentials_json = auth_config["service_account_json"]
                    if isinstance(credentials_json, str):
                        json.loads(credentials_json)
                except json.JSONDecodeError:
                    errors.append("Invalid service account JSON format")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
        }

    @staticmethod
    def test_connection(
        auth_config: dict[str, Any], project_id: str = None
    ) -> dict[str, Any]:
        """
        Test BigQuery connection.

        Args:
            auth_config: Authentication configuration
            project_id: Optional project ID override

        Returns:
            Test result
        """
        try:
            from google.cloud import bigquery

            # Get credentials
            credentials_config = BigQueryAuth.get_credentials_from_config(auth_config)

            # Create client
            if credentials_config.get("credentials") == "default":
                client = bigquery.Client(project=project_id)
            else:
                from google.oauth2 import service_account

                credentials = service_account.Credentials.from_service_account_info(
                    credentials_config["credentials"]
                )
                client = bigquery.Client(
                    credentials=credentials,
                    project=project_id or credentials_config.get("project_id"),
                )

            # Test connection with a simple query
            query = "SELECT 1 as test_connection"
            job = client.query(query)
            list(job.result())  # Execute query

            return {
                "success": True,
                "message": "BigQuery connection successful",
                "details": {
                    "project_id": client.project,
                    "location": getattr(client, "location", "default"),
                },
            }

        except ImportError:
            return {
                "success": False,
                "message": "google-cloud-bigquery package not installed",
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"BigQuery connection failed: {str(e)}",
                "error": str(e),
            }

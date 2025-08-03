"""
BigQuery Authentication
"""

import logging
from typing import Any

from app.models.auth import AuthMethod

logger = logging.getLogger(__name__)


class BigQueryAuth:
    """BigQuery authentication handler."""

    # BigQuery authentication - only what makes sense for web UI
    SUPPORTED_METHODS = [
        AuthMethod.SERVICE_ACCOUNT,  # JSON key file - the standard way
    ]
    DEFAULT_METHOD = AuthMethod.SERVICE_ACCOUNT

    # Auth field definitions for UI
    AUTH_FIELDS = {
        AuthMethod.SERVICE_ACCOUNT: {
            "credentials": {
                "required": True,
                "type": "json_upload",
                "placeholder": '{\n  "type": "service_account",\n  "project_id": "your-project",\n  "private_key_id": "...",\n  "private_key": "-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----\\n",\n  "client_email": "...@...iam.gserviceaccount.com",\n  "client_id": "...",\n  "auth_uri": "https://accounts.google.com/o/oauth2/auth",\n  "token_uri": "https://oauth2.googleapis.com/token",\n  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",\n  "client_x509_cert_url": "..."\n}',
                "description": "Service account JSON key (download from GCP Console > IAM & Admin > Service Accounts)",
            }
        }
    }

    @staticmethod
    def get_credentials_from_config(auth_config: dict[str, Any]) -> dict[str, Any]:
        """
        Get BigQuery credentials from auth configuration.

        Args:
            auth_config: Authentication configuration

        Returns:
            Credentials dictionary for DLT BigQuery destination
        """
        auth_method = auth_config.get("method", AuthMethod.SERVICE_ACCOUNT)

        # Handle both string and enum values for backward compatibility
        if isinstance(auth_method, str):
            try:
                auth_method = AuthMethod(auth_method)
            except ValueError:
                # Map legacy values
                if auth_method == "service_account":
                    auth_method = AuthMethod.SERVICE_ACCOUNT
                else:
                    raise ValueError(
                        f"Unsupported BigQuery auth method: {auth_method}. Only SERVICE_ACCOUNT is supported."
                    ) from None

        if auth_method == AuthMethod.SERVICE_ACCOUNT:
            return BigQueryAuth._get_service_account_credentials(auth_config)
        else:
            raise ValueError(
                f"Unsupported BigQuery auth method: {auth_method}. Only SERVICE_ACCOUNT is supported."
            )

    @staticmethod
    def _get_service_account_credentials(auth_config: dict[str, Any]) -> dict[str, Any]:
        """Get service account credentials."""
        credentials_json = auth_config.get("credentials")
        if not credentials_json:
            raise ValueError("credentials is required for service_account auth")

        # Use credentials directly as dict
        if isinstance(credentials_json, dict):
            credentials_dict = credentials_json
        else:
            raise ValueError(
                f"credentials must be a JSON object, got {type(credentials_json)}"
            )

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
        else:
            # Handle both string and enum values
            if isinstance(auth_method, str):
                try:
                    auth_method_enum = AuthMethod(auth_method)
                except ValueError:
                    # Map legacy values
                    if auth_method == "service_account":
                        auth_method_enum = AuthMethod.SERVICE_ACCOUNT
                    else:
                        errors.append(
                            f"Unsupported auth method: {auth_method}. Only SERVICE_ACCOUNT is supported."
                        )
                        return {"valid": len(errors) == 0, "errors": errors}
            else:
                auth_method_enum = auth_method

            if auth_method_enum != AuthMethod.SERVICE_ACCOUNT:
                errors.append(
                    f"Unsupported auth method: {auth_method_enum}. Only SERVICE_ACCOUNT is supported."
                )
            else:
                if not auth_config.get("credentials"):
                    errors.append("credentials is required for service_account auth")
                else:
                    # Validate credentials structure
                    credentials_json = auth_config["credentials"]
                    if not isinstance(credentials_json, dict):
                        errors.append("credentials must be a JSON object")

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

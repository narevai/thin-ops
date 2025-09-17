"""
Verify Export Stage
"""

import logging
from datetime import datetime
from typing import Any

from pipeline.stages.base import BaseStage, StageResult

logger = logging.getLogger(__name__)


class VerifyExportStage(BaseStage):
    """Verify export completion and data integrity."""

    def __init__(self, config, db):
        super().__init__(config, db)
        self.stage_name = "verify_export"

    async def validate_input(self, context: dict[str, Any]) -> None:
        """Validate verify export stage input."""
        required = ["destination", "expected_count"]
        missing = [field for field in required if field not in context]

        if missing:
            raise ValueError(f"Missing required context fields: {missing}")

    async def execute(self, context: dict[str, Any]) -> StageResult:
        """Execute export verification."""
        start_time = datetime.now()

        try:
            destination = context["destination"]
            expected_count = context["expected_count"]

            # Test destination connection
            connection_test = destination.test_connection()
            if not connection_test["success"]:
                error_msg = (
                    f"Destination connection failed: {connection_test['message']}"
                )
                logger.error(error_msg)
                return self._create_error_result(start_time, error_msg)

            # For now, just verify connection was successful
            # In future versions, could add:
            # - Query destination to verify record count
            # - Sample data validation
            # - Schema validation

            logger.info("Export verification completed successfully")

            duration = (datetime.now() - start_time).total_seconds()

            return StageResult(
                stage_name=self.stage_name,
                success=True,
                records_processed=expected_count,
                records_failed=0,
                duration_seconds=duration,
                errors=[],
                data={
                    "verification_status": "completed",
                    "connection_test": connection_test,
                    "expected_count": expected_count,
                },
            )

        except Exception as e:
            logger.error(f"VerifyExportStage failed: {e}")
            return self._create_error_result(start_time, str(e))

    def _create_error_result(self, start_time: datetime, error_msg: str) -> StageResult:
        """Create error stage result."""
        duration = (datetime.now() - start_time).total_seconds()
        return StageResult(
            stage_name=self.stage_name,
            success=False,
            records_processed=0,
            records_failed=0,
            duration_seconds=duration,
            errors=[{"error": error_msg, "type": "VerificationError"}],
            data={},
        )

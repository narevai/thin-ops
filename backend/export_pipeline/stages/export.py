"""
Export Stage
"""

import logging
from datetime import datetime
from typing import Any

import dlt

from pipeline.stages.base import BaseStage, StageResult

logger = logging.getLogger(__name__)


class ExportStage(BaseStage):
    """Execute data export using DLT."""

    def __init__(self, config, db):
        super().__init__(config, db)
        self.stage_name = "export"

    async def validate_input(self, context: dict[str, Any]) -> None:
        """Validate export stage input."""
        required = ["export_records", "destination", "pipeline_name"]
        missing = [field for field in required if field not in context]

        if missing:
            raise ValueError(f"Missing required context fields: {missing}")

    async def execute(self, context: dict[str, Any]) -> StageResult:
        """Execute data export via DLT."""
        start_time = datetime.now()
        records_processed = 0

        try:
            records = context["export_records"]
            destination = context["destination"]
            pipeline_name = context["pipeline_name"]
            dataset_name = context.get("dataset_name", "narev_exports")

            if not records:
                logger.warning("No records to export")
                return self._create_success_result(start_time, 0)

            # Prepare DLT pipeline
            pipeline = destination.prepare_dlt_pipeline(pipeline_name, dataset_name)
            schema = destination.get_export_schema()

            # Create DLT source
            table_name = schema.get("table_name", "billing_data_export")

            @dlt.resource(
                name=table_name,
                write_disposition=schema.get("write_disposition", "append"),
                primary_key=schema.get("primary_key", ["id"]),
            )
            def export_data():
                """DLT resource for export data."""
                yield records

            # Run DLT pipeline
            logger.info(
                f"Starting DLT export: {len(records)} records to {destination.destination_type}"
            )
            load_info = pipeline.run(export_data())

            # Check for errors
            if load_info.has_failed_jobs:
                failed_jobs = [
                    job
                    for job in load_info.load_packages[0].jobs.values()
                    if job.job_file_info.state == "failed"
                ]
                error_msg = f"DLT export failed: {len(failed_jobs)} failed jobs"
                logger.error(error_msg)

                return self._create_error_result(
                    start_time, records_processed, error_msg
                )

            records_processed = len(records)
            logger.info(
                f"DLT export completed successfully: {records_processed} records"
            )

            duration = (datetime.now() - start_time).total_seconds()

            return StageResult(
                stage_name=self.stage_name,
                success=True,
                records_processed=records_processed,
                records_failed=0,
                duration_seconds=duration,
                errors=[],
                data={
                    "load_info": {
                        "load_id": load_info.loads_ids[-1]
                        if load_info.loads_ids
                        else None,
                        "package_info": str(load_info.load_packages[0])
                        if load_info.load_packages
                        else None,
                    }
                },
            )

        except Exception as e:
            logger.error(f"ExportStage failed: {e}")
            return self._create_error_result(start_time, records_processed, str(e))

    def _create_success_result(
        self, start_time: datetime, records_processed: int
    ) -> StageResult:
        """Create successful stage result."""
        duration = (datetime.now() - start_time).total_seconds()
        return StageResult(
            stage_name=self.stage_name,
            success=True,
            records_processed=records_processed,
            records_failed=0,
            duration_seconds=duration,
            errors=[],
            data={},
        )

    def _create_error_result(
        self, start_time: datetime, records_processed: int, error_msg: str
    ) -> StageResult:
        """Create error stage result."""
        duration = (datetime.now() - start_time).total_seconds()
        return StageResult(
            stage_name=self.stage_name,
            success=False,
            records_processed=records_processed,
            records_failed=0,
            duration_seconds=duration,
            errors=[{"error": error_msg, "type": "ExportError"}],
            data={},
        )

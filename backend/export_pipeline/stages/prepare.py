"""
Prepare Export Stage
"""

import logging
from datetime import datetime
from typing import Any

from sqlalchemy import text

from pipeline.stages.base import BaseStage, StageResult

logger = logging.getLogger(__name__)


class PrepareExportStage(BaseStage):
    """Prepare data for export from billing_data table."""

    def __init__(self, config, db):
        super().__init__(config, db)
        self.stage_name = "prepare_export"

    async def validate_input(self, context: dict[str, Any]) -> None:
        """Validate prepare export stage input."""
        required = ["export_filters", "destination"]
        missing = [field for field in required if field not in context]

        if missing:
            raise ValueError(f"Missing required context fields: {missing}")

    async def execute(self, context: dict[str, Any]) -> StageResult:
        """Execute data preparation for export."""
        start_time = datetime.now()
        records_processed = 0
        records = []

        try:
            export_filters = context["export_filters"]
            destination = context["destination"]

            # Build SQL query with filters
            query = self._build_export_query(export_filters)

            # Execute query in batches
            batch_size = self.get_batch_size()
            offset = 0

            while True:
                paginated_query = f"{query} LIMIT {batch_size} OFFSET {offset}"
                result = self.db.execute(text(paginated_query))
                batch_records = [dict(row._mapping) for row in result.fetchall()]

                if not batch_records:
                    break

                # Transform records for destination
                transformed_batch = destination.transform_for_destination(batch_records)
                records.extend(transformed_batch)
                records_processed += len(batch_records)

                logger.info(
                    f"Processed batch: {len(batch_records)} records (total: {records_processed})"
                )

                offset += batch_size

                # Break if batch is smaller than expected (last batch)
                if len(batch_records) < batch_size:
                    break

            duration = (datetime.now() - start_time).total_seconds()

            return StageResult(
                stage_name=self.stage_name,
                success=True,
                records_processed=records_processed,
                records_failed=0,
                duration_seconds=duration,
                errors=[],
                data={"export_records": records, "total_count": records_processed},
            )

        except Exception as e:
            logger.error(f"PrepareExportStage failed: {e}")
            duration = (datetime.now() - start_time).total_seconds()

            return StageResult(
                stage_name=self.stage_name,
                success=False,
                records_processed=records_processed,
                records_failed=0,
                duration_seconds=duration,
                errors=[{"error": str(e), "type": type(e).__name__}],
                data={},
            )

    def _build_export_query(self, filters: dict[str, Any]) -> str:
        """Build SQL query based on export filters."""
        base_query = "SELECT * FROM billing_data WHERE 1=1"
        conditions = []

        # Date range filters
        if filters.get("start_date"):
            conditions.append(f"charge_period_start >= '{filters['start_date']}'")
        if filters.get("end_date"):
            conditions.append(f"charge_period_end <= '{filters['end_date']}'")

        # Provider filter
        if filters.get("provider_id"):
            conditions.append(f"x_provider_id = '{filters['provider_id']}'")

        # Service filters
        if filters.get("service_category"):
            conditions.append(f"service_category = '{filters['service_category']}'")
        if filters.get("service_name"):
            conditions.append(f"service_name = '{filters['service_name']}'")

        # Cost filters
        if filters.get("min_cost"):
            conditions.append(f"billed_cost >= {filters['min_cost']}")
        if filters.get("max_cost"):
            conditions.append(f"billed_cost <= {filters['max_cost']}")

        # Combine conditions
        if conditions:
            base_query += " AND " + " AND ".join(conditions)

        # Add ordering
        base_query += " ORDER BY charge_period_start, id"

        return base_query

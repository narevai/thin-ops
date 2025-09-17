"""
Export Pipeline Hamilton Orchestrator
"""

import asyncio
import logging
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from hamilton import driver
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.export_run import ExportRun
from app.services.encryption_service import EncryptionService
from export_destinations.registry import ExportDestinationRegistry
from export_pipeline.stages.export import ExportStage
from export_pipeline.stages.prepare import PrepareExportStage
from export_pipeline.stages.verify import VerifyExportStage
from pipeline.config import PipelineConfig
from pipeline.stages.base import StageResult

logger = logging.getLogger(__name__)


# =============================================================================
# Hamilton DAG Functions
# =============================================================================


def export_context(
    destination_id: UUID,
    export_filters: dict[str, Any],
    export_run_id: UUID,
    destination_config: dict[str, Any],
    pipeline_config: PipelineConfig,
    db_session: Session,
) -> dict[str, Any]:
    """Initialize export context - ROOT NODE of Hamilton DAG."""
    destination_type = destination_config["destination_type"]

    # Create destination instance
    destination = ExportDestinationRegistry.create_destination(
        destination_type, destination_config
    )
    if not destination:
        raise ValueError(
            f"Failed to create destination instance for type: {destination_type}"
        )

    return {
        "export_run_id": export_run_id,
        "destination_id": destination_id,
        "export_filters": export_filters,
        "destination_config": destination_config,
        "destination": destination,
        "destination_type": destination_type,
        "pipeline_config": pipeline_config,
        "db_session": db_session,
        "pipeline_name": f"narev_export_{destination_type}_{export_run_id}",
        "dataset_name": destination_config.get("destination_config", {}).get(
            "dataset_id", "narev_exports"
        ),
    }


def prepare_export_result(export_context: dict[str, Any]) -> StageResult:
    """Prepare export data stage."""
    logger.info("Hamilton: Starting prepare export stage")

    pipeline_config = export_context["pipeline_config"]
    db_session = export_context["db_session"]

    stage = PrepareExportStage(pipeline_config, db_session)

    try:
        result = asyncio.run(stage.execute(export_context))
    except RuntimeError as e:
        if "asyncio.run() cannot be called from a running event loop" in str(e):
            logger.warning("Using fallback event loop handling")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(stage.execute(export_context))
            finally:
                loop.close()
        else:
            raise

    logger.info(
        f"Hamilton: Prepare export stage completed - {result.records_processed} records"
    )
    return result


def export_stage_result(
    prepare_export_result: StageResult, export_context: dict[str, Any]
) -> StageResult:
    """Export data stage via DLT."""
    logger.info("Hamilton: Starting export stage")

    pipeline_config = export_context["pipeline_config"]
    db_session = export_context["db_session"]

    # Update context with prepared data
    updated_context = {**export_context}
    if prepare_export_result.success and prepare_export_result.data:
        updated_context.update(prepare_export_result.data)

    stage = ExportStage(pipeline_config, db_session)

    try:
        result = asyncio.run(stage.execute(updated_context))
    except RuntimeError as e:
        if "asyncio.run() cannot be called from a running event loop" in str(e):
            logger.warning("Using fallback event loop handling")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(stage.execute(updated_context))
            finally:
                loop.close()
        else:
            raise

    logger.info(
        f"Hamilton: Export stage completed - {result.records_processed} records"
    )
    return result


def verify_export_result(
    export_stage_result: StageResult, export_context: dict[str, Any]
) -> StageResult:
    """Verify export completion stage."""
    logger.info("Hamilton: Starting verify export stage")

    pipeline_config = export_context["pipeline_config"]
    db_session = export_context["db_session"]

    # Update context with export results
    updated_context = {**export_context}
    if export_stage_result.success:
        updated_context["expected_count"] = export_stage_result.records_processed
    else:
        updated_context["expected_count"] = 0

    stage = VerifyExportStage(pipeline_config, db_session)

    try:
        result = asyncio.run(stage.execute(updated_context))
    except RuntimeError as e:
        if "asyncio.run() cannot be called from a running event loop" in str(e):
            logger.warning("Using fallback event loop handling")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(stage.execute(updated_context))
            finally:
                loop.close()
        else:
            raise

    logger.info("Hamilton: Verify export stage completed")
    return result


def export_pipeline_result(
    prepare_export_result: StageResult,
    export_stage_result: StageResult,
    verify_export_result: StageResult,
    export_context: dict[str, Any],
) -> dict[str, Any]:
    """Final export pipeline result aggregation."""
    export_run_id = export_context["export_run_id"]
    destination_id = export_context["destination_id"]

    # Determine final status
    all_success = all(
        [
            prepare_export_result.success,
            export_stage_result.success,
            verify_export_result.success,
        ]
    )

    final_status = "completed" if all_success else "failed"

    return {
        "export_run_id": str(export_run_id),
        "destination_id": str(destination_id),
        "status": final_status,
        "stages": {
            "prepare": {
                "success": prepare_export_result.success,
                "records_processed": prepare_export_result.records_processed,
                "duration": prepare_export_result.duration_seconds,
                "errors": prepare_export_result.errors[:3],
            },
            "export": {
                "success": export_stage_result.success,
                "records_processed": export_stage_result.records_processed,
                "duration": export_stage_result.duration_seconds,
                "errors": export_stage_result.errors[:3],
            },
            "verify": {
                "success": verify_export_result.success,
                "duration": verify_export_result.duration_seconds,
                "errors": verify_export_result.errors[:3],
            },
        },
        "totals": {
            "total_records_exported": export_stage_result.records_processed,
            "total_duration": (
                prepare_export_result.duration_seconds
                + export_stage_result.duration_seconds
                + verify_export_result.duration_seconds
            ),
            "stages_completed": sum(
                [
                    prepare_export_result.success,
                    export_stage_result.success,
                    verify_export_result.success,
                ]
            ),
        },
    }


# =============================================================================
# Export Orchestrator Class
# =============================================================================


class ExportOrchestrator:
    """Hamilton-based export pipeline orchestrator."""

    def __init__(self, config: PipelineConfig | None = None):
        """Initialize export orchestrator."""
        self.config = config or PipelineConfig()
        self.encryption_service = EncryptionService()
        self.driver = self._create_hamilton_driver()
        logger.info("Export orchestrator initialized")

    def _create_hamilton_driver(self) -> driver.Driver:
        """Create Hamilton driver with export DAG functions."""
        import sys

        current_module = sys.modules[__name__]
        return driver.Builder().with_modules(current_module).build()

    async def run_export(
        self,
        destination_id: UUID,
        export_filters: dict[str, Any],
        export_type: str = "filtered",
    ) -> dict[str, Any]:
        """
        Run export pipeline using Hamilton DAG.

        Args:
            destination_id: Export destination ID
            export_filters: Filters for data export
            export_type: Type of export (full, incremental, filtered)

        Returns:
            Export result dictionary
        """
        export_run_id = uuid4()
        db = SessionLocal()

        try:
            # Initialize export run
            destination_config, export_run = await self._initialize_export(
                db, destination_id, export_run_id, export_type, export_filters
            )

            # Prepare Hamilton inputs
            inputs = {
                "destination_id": destination_id,
                "export_filters": export_filters,
                "export_run_id": export_run_id,
                "destination_config": destination_config,
                "pipeline_config": self.config,
                "db_session": db,
            }

            # Execute Hamilton DAG in thread pool
            logger.info(
                f"Hamilton: Executing export DAG for destination {destination_config['name']}"
            )

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, self._execute_hamilton_sync, inputs
            )

            # Extract final result
            pipeline_result = result["export_pipeline_result"]

            # Update export run with results
            final_status = pipeline_result["status"]
            await self._finalize_export(db, export_run, final_status, pipeline_result)

            logger.info(
                f"Hamilton: Export {export_run_id} completed with status: {final_status}"
            )
            return pipeline_result

        except Exception as e:
            logger.error(
                f"Hamilton: Export failed for destination {destination_id}: {e}"
            )
            await self._handle_export_error(db, locals().get("export_run"), str(e))
            raise
        finally:
            db.close()

    def _execute_hamilton_sync(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """Execute Hamilton DAG synchronously."""
        try:
            result = self.driver.execute(
                ["export_pipeline_result"],
                inputs=inputs,
                overrides={},
            )
            return result
        except Exception as e:
            logger.error(f"Hamilton synchronous execution failed: {e}")
            raise

    async def _initialize_export(
        self, db, destination_id, export_run_id, export_type, export_filters
    ):
        """Initialize export run and get destination configuration."""
        destination_config = await self._get_destination_config(db, destination_id)
        if not destination_config:
            raise ValueError(
                f"Export destination {destination_id} not found or not configured"
            )

        export_run = await self._create_export_run(
            db, destination_id, export_run_id, export_type, export_filters
        )

        logger.info(
            f"Hamilton: Initialized export {export_run_id} for destination {destination_config['name']}"
        )
        return destination_config, export_run

    async def _create_export_run(
        self, db, destination_id, export_run_id, export_type, export_filters
    ):
        """Create export run with retry logic."""
        max_retries = 3

        for attempt in range(max_retries):
            try:
                export_run = ExportRun(
                    id=str(export_run_id),
                    destination_id=str(destination_id),
                    export_type=export_type,
                    status="running",
                    filters=export_filters,
                    started_at=self._utcnow(),
                    dlt_pipeline_name=f"narev_export_{export_run_id}",
                )

                db.add(export_run)
                db.commit()
                db.refresh(export_run)
                return export_run

            except IntegrityError:
                db.rollback()
                if attempt < max_retries - 1:
                    logger.warning(
                        f"Database conflict on attempt {attempt + 1}, retrying..."
                    )
                    export_run_id = uuid4()
                    await asyncio.sleep(0.1 * (attempt + 1))
                    continue
                else:
                    raise
            except Exception:
                db.rollback()
                raise

        raise Exception(f"Failed to create export run after {max_retries} attempts")

    async def _finalize_export(self, db, export_run, final_status, pipeline_result):
        """Finalize export run with results."""
        try:
            db.refresh(export_run)

            export_run.status = final_status
            export_run.completed_at = self._utcnow()

            if "totals" in pipeline_result:
                totals = pipeline_result["totals"]
                export_run.records_exported = str(
                    totals.get("total_records_exported", 0)
                )
                export_run.duration_seconds = str(int(totals.get("total_duration", 0)))

            db.commit()

        except Exception as e:
            db.rollback()
            logger.error(f"Hamilton: Failed to finalize export run: {e}")

    async def _handle_export_error(self, db, export_run, error_message):
        """Handle export-level errors."""
        if export_run:
            try:
                db.refresh(export_run)
                export_run.status = "failed"
                export_run.error_message = error_message
                db.commit()
            except Exception as update_error:
                logger.error(
                    f"Hamilton: Failed to update export run on error: {update_error}"
                )

    async def _get_destination_config(self, db, destination_id):
        """Get destination configuration from database."""
        from app.services.export_destination_service import ExportDestinationService

        service = ExportDestinationService(db)
        return service.get_destination_config(destination_id)

    def _utcnow(self) -> datetime:
        """Get current UTC time with timezone info."""
        return datetime.now(UTC)

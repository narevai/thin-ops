"""
Export Run Model
"""

from uuid import uuid4

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.config import get_settings
from app.database import Base

settings = get_settings()


def get_json_field():
    """Get appropriate JSON field type based on database."""
    from sqlalchemy import JSON

    return JSONB if settings.is_postgres else JSON


class ExportRun(Base):
    """Export run execution tracking."""

    __tablename__ = "export_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    destination_id = Column(
        String(36), ForeignKey("export_destinations.id"), nullable=False
    )

    # Export metadata
    export_type = Column(
        String(50), nullable=False
    )  # 'full', 'incremental', 'filtered'
    status = Column(String(50), nullable=False)  # 'running', 'completed', 'failed'

    # Date range
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))

    # Filters
    filters = Column(get_json_field())

    # Results
    records_exported = Column(String(50))  # Use string to handle large numbers
    records_failed = Column(String(50))
    export_size_bytes = Column(String(50))

    # Timing
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    duration_seconds = Column(String(50))

    # Error tracking
    error_message = Column(Text)
    error_details = Column(get_json_field())

    # DLT specific
    dlt_pipeline_name = Column(String(200))
    dlt_load_id = Column(String(200))

    # Relationship
    destination = relationship("ExportDestination", back_populates="export_runs")

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "destination_id": self.destination_id,
            "export_type": self.export_type,
            "status": self.status,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "filters": self.filters,
            "records_exported": self.records_exported,
            "records_failed": self.records_failed,
            "export_size_bytes": self.export_size_bytes,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat()
            if self.completed_at
            else None,
            "duration_seconds": self.duration_seconds,
            "error_message": self.error_message,
            "dlt_pipeline_name": self.dlt_pipeline_name,
            "dlt_load_id": self.dlt_load_id,
        }

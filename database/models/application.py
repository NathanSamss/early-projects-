"""
database/models/application.py
Tracks the submission state of a job application through the pipeline.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey
from database.models.base import Base


# Status values used across the pipeline
STATUS_PENDING   = "pending"          # matched, awaiting tailor
STATUS_TAILORED  = "tailored"         # content ready, awaiting apply
STATUS_APPLIED   = "applied"          # submitted automatically
STATUS_MANUAL    = "pending_manual"   # needs human to finish (CAPTCHA, Workday)
STATUS_FAILED    = "failed"           # submission failed
STATUS_SKIPPED   = "skipped"          # below score threshold


class Application(Base):
    __tablename__ = "applications"

    job_id     = Column(String(16), ForeignKey("jobs.id"), primary_key=True)
    track      = Column(String(20), default="")
    status     = Column(String(30), default=STATUS_PENDING)
    platform   = Column(String(50), default="")
    notes      = Column(String(500), default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "track": self.track,
            "status": self.status,
            "platform": self.platform,
            "notes": self.notes,
        }

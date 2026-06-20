"""
database/models/tailored.py
AI-generated tailored summary and cover letter for a specific job.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from database.models.base import Base


class TailoredContent(Base):
    __tablename__ = "tailored_content"

    job_id       = Column(String(16), ForeignKey("jobs.id"), primary_key=True)
    summary      = Column(Text, default="")
    cover_letter = Column(Text, default="")
    created_at   = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "summary": self.summary,
            "cover_letter": self.cover_letter,
        }

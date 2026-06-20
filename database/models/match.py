"""
database/models/match.py
The result of scoring a job against a track. One match per job.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from database.models.base import Base


class Match(Base):
    __tablename__ = "matches"

    job_id     = Column(String(16), ForeignKey("jobs.id"), primary_key=True)
    track      = Column(String(20), default="")        # security | ai | edge
    score      = Column(Integer, default=0)            # 0-10
    matched_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {"job_id": self.job_id, "track": self.track, "score": self.score}

"""
database/models/job.py
A scraped job listing. The job_id is a deterministic hash so the same job
from two scraper runs collapses to one row.
"""

import hashlib
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, Float
from database.models.base import Base


class Job(Base):
    __tablename__ = "jobs"

    id          = Column(String(16), primary_key=True)   # deterministic hash
    title       = Column(String(300), nullable=False)
    company     = Column(String(300), nullable=False)
    location    = Column(String(300), default="Remote")
    description = Column(Text, default="")
    url         = Column(String(2000), default="")
    source      = Column(String(50), default="")
    track       = Column(String(20), default="")          # security | ai | edge
    salary      = Column(String(100), nullable=True)
    posted_date = Column(String(100), nullable=True)
    discovered_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    @staticmethod
    def make_id(title: str, company: str, url: str) -> str:
        raw = f"{title}|{company}|{url}".lower()
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "description": self.description,
            "url": self.url,
            "source": self.source,
            "track": self.track,
            "salary": self.salary,
            "posted_date": self.posted_date,
        }

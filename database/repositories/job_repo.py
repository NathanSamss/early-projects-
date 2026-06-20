"""
database/repositories/job_repo.py
All database access for Job rows lives here. Services never write raw SQL —
they call these methods. This is what makes swapping SQLite for Postgres
later a non-event.
"""

import logging
from typing import List, Optional
from database.models.base import get_session
from database.models.job import Job

log = logging.getLogger(__name__)


class JobRepository:

    def upsert(self, data: dict) -> Optional[str]:
        """
        Insert a job if its deterministic id is new. Returns the job_id if
        newly inserted, None if it already existed (deduplication).
        """
        job_id = Job.make_id(data["title"], data["company"], data["url"])
        session = get_session()
        try:
            existing = session.get(Job, job_id)
            if existing:
                return None
            job = Job(
                id=job_id,
                title=data["title"],
                company=data["company"],
                location=data.get("location", "Remote"),
                description=data.get("description", ""),
                url=data.get("url", ""),
                source=data.get("source", ""),
                track=data.get("track", ""),
                salary=data.get("salary"),
                posted_date=data.get("posted_date"),
            )
            session.add(job)
            session.commit()
            return job_id
        except Exception as e:
            session.rollback()
            log.error(f"[job_repo] upsert error: {e}")
            return None
        finally:
            session.close()

    def get(self, job_id: str) -> Optional[Job]:
        session = get_session()
        try:
            return session.get(Job, job_id)
        finally:
            session.close()

    def exists(self, job_id: str) -> bool:
        session = get_session()
        try:
            return session.get(Job, job_id) is not None
        finally:
            session.close()

    def all(self) -> List[Job]:
        session = get_session()
        try:
            return session.query(Job).order_by(Job.discovered_at.desc()).all()
        finally:
            session.close()

    def by_track(self, track: str) -> List[Job]:
        session = get_session()
        try:
            return session.query(Job).filter(Job.track == track).all()
        finally:
            session.close()

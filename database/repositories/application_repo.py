"""
database/repositories/application_repo.py
Database access for Application rows.
"""

import logging
from typing import List, Optional, Dict
from database.models.base import get_session
from database.models.application import Application, STATUS_PENDING

log = logging.getLogger(__name__)


class ApplicationRepository:

    def upsert(self, job_id: str, track: str = "", status: str = STATUS_PENDING,
               platform: str = "", notes: str = "") -> None:
        session = get_session()
        try:
            existing = session.get(Application, job_id)
            if existing:
                existing.status = status
                if track:    existing.track = track
                if platform: existing.platform = platform
                if notes:    existing.notes = notes
            else:
                session.add(Application(
                    job_id=job_id, track=track, status=status,
                    platform=platform, notes=notes,
                ))
            session.commit()
        except Exception as e:
            session.rollback()
            log.error(f"[application_repo] upsert error: {e}")
        finally:
            session.close()

    def get(self, job_id: str) -> Optional[Application]:
        session = get_session()
        try:
            return session.get(Application, job_id)
        finally:
            session.close()

    def all(self) -> List[Application]:
        session = get_session()
        try:
            return session.query(Application).order_by(Application.created_at.desc()).all()
        finally:
            session.close()

    def by_status(self, status: str) -> List[Application]:
        session = get_session()
        try:
            return session.query(Application).filter(Application.status == status).all()
        finally:
            session.close()

    def stats(self) -> Dict[str, int]:
        session = get_session()
        try:
            rows = session.query(Application.status).all()
            counts: Dict[str, int] = {}
            for (status,) in rows:
                counts[status] = counts.get(status, 0) + 1
            return counts
        finally:
            session.close()

"""
database/repositories/tailored_repo.py
Database access for TailoredContent rows.
"""

import logging
from typing import Optional
from database.models.base import get_session
from database.models.tailored import TailoredContent

log = logging.getLogger(__name__)


class TailoredRepository:

    def save(self, job_id: str, summary: str, cover_letter: str) -> None:
        session = get_session()
        try:
            existing = session.get(TailoredContent, job_id)
            if existing:
                existing.summary = summary
                existing.cover_letter = cover_letter
            else:
                session.add(TailoredContent(
                    job_id=job_id, summary=summary, cover_letter=cover_letter
                ))
            session.commit()
        except Exception as e:
            session.rollback()
            log.error(f"[tailored_repo] save error: {e}")
        finally:
            session.close()

    def get(self, job_id: str) -> Optional[TailoredContent]:
        session = get_session()
        try:
            return session.get(TailoredContent, job_id)
        finally:
            session.close()

"""
database/repositories/match_repo.py
Database access for Match rows.
"""

import logging
from typing import List, Optional
from database.models.base import get_session
from database.models.match import Match

log = logging.getLogger(__name__)


class MatchRepository:

    def save(self, job_id: str, track: str, score: int) -> None:
        session = get_session()
        try:
            existing = session.get(Match, job_id)
            if existing:
                existing.track = track
                existing.score = score
            else:
                session.add(Match(job_id=job_id, track=track, score=score))
            session.commit()
        except Exception as e:
            session.rollback()
            log.error(f"[match_repo] save error: {e}")
        finally:
            session.close()

    def get(self, job_id: str) -> Optional[Match]:
        session = get_session()
        try:
            return session.get(Match, job_id)
        finally:
            session.close()

    def above_score(self, min_score: int) -> List[Match]:
        session = get_session()
        try:
            return session.query(Match).filter(Match.score >= min_score).all()
        finally:
            session.close()

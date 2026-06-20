"""
services/analytics/analytics_service.py
Aggregates application stats for the dashboard and summary emails.
Breaks results down by track so you can see which track performs best.
"""

import logging
from typing import Dict, Any
from database.repositories.application_repo import ApplicationRepository
from database.repositories.job_repo import JobRepository

log = logging.getLogger(__name__)


class AnalyticsService:
    def __init__(self) -> None:
        self.app_repo = ApplicationRepository()
        self.job_repo = JobRepository()

    def summary(self) -> Dict[str, Any]:
        status_counts = self.app_repo.stats()
        by_track: Dict[str, int] = {}
        for app in self.app_repo.all():
            by_track[app.track] = by_track.get(app.track, 0) + 1
        return {
            "total_applications": sum(status_counts.values()),
            "by_status": status_counts,
            "by_track": by_track,
        }

"""
services/discovery/discovery_service.py
Runs all sources for all track keywords, classifies each job into a track,
and persists new jobs via the repository. Returns the list of new job_ids.
"""

import logging
from typing import List

from services.discovery.remotive_source import RemotiveSource
from services.discovery.jobicy_source import JobicySource
from services.matching.tracks import classify
from database.repositories.job_repo import JobRepository

log = logging.getLogger(__name__)

# Keywords per track — drives what we search for
TRACK_KEYWORDS = {
    "security": ["cybersecurity analyst", "soc analyst", "security engineer",
                 "information security", "threat analyst"],
    "ai":       ["machine learning engineer", "ai engineer", "data scientist",
                 "mlops engineer", "ml engineer"],
    "edge":     ["embedded systems engineer", "edge ai", "robotics engineer",
                 "computer vision engineer", "tinyml"],
}


class DiscoveryService:
    def __init__(self) -> None:
        self.sources = [RemotiveSource(), JobicySource()]
        self.repo = JobRepository()

    def run(self) -> List[str]:
        """Scrape all sources for all keywords, classify, persist new jobs."""
        new_ids: List[str] = []
        all_keywords = [kw for kws in TRACK_KEYWORDS.values() for kw in kws]

        for source in self.sources:
            for keyword in all_keywords:
                try:
                    raw_jobs = source.fetch(keyword)
                except Exception as e:
                    log.error(f"[discovery] {source.name} failed on '{keyword}': {e}")
                    continue

                for raw in raw_jobs:
                    text = f"{raw['title']} {raw['description']}"
                    track = classify(text)
                    if not track:
                        continue  # fits no track, drop it
                    raw["track"] = track
                    job_id = self.repo.upsert(raw)
                    if job_id:
                        new_ids.append(job_id)

        log.info(f"[discovery] {len(new_ids)} new jobs persisted")
        return new_ids

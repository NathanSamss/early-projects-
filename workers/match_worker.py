"""
workers/match_worker.py
Stage 2: score a job against its track. Good matches go to the tailor queue,
weak ones are recorded as skipped.
"""
import logging
from services.matching.matcher import score
from services.resume_generation.resume_service import ResumeService
from database.repositories.job_repo import JobRepository
from database.repositories.match_repo import MatchRepository
from database.repositories.application_repo import ApplicationRepository
from database.models.application import STATUS_PENDING, STATUS_SKIPPED
from config import APPLY_SETTINGS
from workers.queues import tailor_queue

log = logging.getLogger(__name__)

_resume = ResumeService()
_job_repo = JobRepository()
_match_repo = MatchRepository()
_app_repo = ApplicationRepository()


def match_job(job_id: str) -> None:
    job = _job_repo.get(job_id)
    if not job:
        log.warning(f"[match_worker] job {job_id} not found")
        return
    base_resume = _resume.load_base()
    track, sc = score(job.to_dict(), base_resume)
    _match_repo.save(job_id, track, sc)

    if sc >= APPLY_SETTINGS["min_match_score"]:
        _app_repo.upsert(job_id, track=track, status=STATUS_PENDING)
        tailor_queue.enqueue("workers.tailor_worker.tailor_job", job_id)
        log.info(f"[match_worker] {job.title} -> {track} {sc}/10 — queued for tailoring")
    else:
        _app_repo.upsert(job_id, track=track, status=STATUS_SKIPPED)
        log.info(f"[match_worker] {job.title} -> {track} {sc}/10 — skipped")

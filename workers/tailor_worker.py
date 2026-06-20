"""
workers/tailor_worker.py
Stage 3: generate tailored summary + cover letter, then hand to apply queue.
"""
import logging
from services.tailoring.tailor_service import TailorService
from services.resume_generation.resume_service import ResumeService
from database.repositories.job_repo import JobRepository
from database.repositories.match_repo import MatchRepository
from database.repositories.tailored_repo import TailoredRepository
from database.repositories.application_repo import ApplicationRepository
from database.models.application import STATUS_TAILORED
from workers.queues import apply_queue

log = logging.getLogger(__name__)

_tailor = TailorService()
_resume = ResumeService()
_job_repo = JobRepository()
_match_repo = MatchRepository()
_tailored_repo = TailoredRepository()
_app_repo = ApplicationRepository()


def tailor_job(job_id: str) -> None:
    job = _job_repo.get(job_id)
    match = _match_repo.get(job_id)
    if not job or not match:
        log.warning(f"[tailor_worker] missing job/match for {job_id}")
        return
    base_resume = _resume.load_base()
    summary, cover = _tailor.tailor(job.to_dict(), match.track, base_resume)
    _tailored_repo.save(job_id, summary, cover)
    _app_repo.upsert(job_id, status=STATUS_TAILORED)
    apply_queue.enqueue("workers.apply_worker.apply_job", job_id)
    log.info(f"[tailor_worker] tailored {job.title} — queued for apply")

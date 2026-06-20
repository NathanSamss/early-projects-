"""
workers/apply_worker.py
Stage 4: route the job to the correct platform adapter and attempt to apply.
Records the outcome. Never auto-submits unless config allows it.
"""
import logging
from adapters.registry import get_adapter
from database.repositories.job_repo import JobRepository
from database.repositories.application_repo import ApplicationRepository
from database.models.application import STATUS_APPLIED, STATUS_MANUAL, STATUS_FAILED
from config import APPLICANT, RESUME_PDF_PATH

log = logging.getLogger(__name__)

_job_repo = JobRepository()
_app_repo = ApplicationRepository()


def apply_job(job_id: str) -> None:
    job = _job_repo.get(job_id)
    if not job:
        log.warning(f"[apply_worker] job {job_id} not found")
        return

    adapter = get_adapter(job.url)
    if not adapter:
        _app_repo.upsert(job_id, status=STATUS_MANUAL, platform="unknown",
                         notes="No adapter for this URL — apply manually")
        log.info(f"[apply_worker] no adapter for {job.url}")
        return

    try:
        result = adapter.apply(job.to_dict(), APPLICANT, RESUME_PDF_PATH)
    except Exception as e:
        _app_repo.upsert(job_id, status=STATUS_FAILED, platform=adapter.platform, notes=str(e))
        log.error(f"[apply_worker] {adapter.platform} raised: {e}")
        return

    if result.submitted:
        status = STATUS_APPLIED
    elif result.needs_manual:
        status = STATUS_MANUAL
    else:
        status = STATUS_FAILED

    _app_repo.upsert(job_id, status=status, platform=result.platform, notes=result.note)
    log.info(f"[apply_worker] {job.title} -> {status} ({result.platform}: {result.note})")

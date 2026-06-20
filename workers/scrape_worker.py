"""
workers/scrape_worker.py
Stage 1: discover jobs, then hand each new job_id to the match queue.
"""
import logging
from services.discovery.discovery_service import DiscoveryService
from workers.queues import match_queue

log = logging.getLogger(__name__)


def run_discovery() -> int:
    """Scrape all sources, enqueue each new job for matching. Returns count."""
    new_ids = DiscoveryService().run()
    for job_id in new_ids:
        match_queue.enqueue("workers.match_worker.match_job", job_id)
    log.info(f"[scrape_worker] enqueued {len(new_ids)} jobs for matching")
    return len(new_ids)

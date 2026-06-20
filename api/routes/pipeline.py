"""api/routes/pipeline.py — trigger and monitor the pipeline."""
import logging
from flask import Blueprint, jsonify
from workers.queues import scrape_queue

log = logging.getLogger(__name__)
pipeline_bp = Blueprint("pipeline", __name__, url_prefix="/pipeline")


@pipeline_bp.post("/run")
def run_pipeline():
    """Kick off stage 1. The queue chain handles the rest."""
    job = scrape_queue.enqueue("workers.scrape_worker.run_discovery")
    return jsonify({"enqueued": True, "task_id": job.id}), 202


@pipeline_bp.get("/status")
def status():
    from workers.queues import match_queue, tailor_queue, apply_queue
    return jsonify({
        "scrape_queue": len(scrape_queue),
        "match_queue":  len(match_queue),
        "tailor_queue": len(tailor_queue),
        "apply_queue":  len(apply_queue),
    })

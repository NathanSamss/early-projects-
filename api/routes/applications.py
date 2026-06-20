"""api/routes/applications.py — read application status and stats, accept extension reports."""
from flask import Blueprint, jsonify, request
from database.repositories.application_repo import ApplicationRepository
from database.repositories.job_repo import JobRepository
from database.models.job import Job
from database.models.application import STATUS_APPLIED
from services.analytics.analytics_service import AnalyticsService

applications_bp = Blueprint("applications", __name__, url_prefix="/applications")
_repo = JobRepository()
_app_repo = ApplicationRepository()
_analytics = AnalyticsService()


@applications_bp.get("/")
def list_applications():
    return jsonify([a.to_dict() for a in _app_repo.all()])


@applications_bp.get("/stats")
def stats():
    return jsonify(_analytics.summary())


@applications_bp.post("/report")
def report():
    """Accept a result from the Chrome extension after it submits an application."""
    data = request.get_json(silent=True) or {}
    url = data.get("url", "")
    status = data.get("status", STATUS_APPLIED)
    platform = data.get("platform", "")
    if not url:
        return jsonify({"error": "url required"}), 400
    # Best-effort: match the URL to a known job, else just record it
    job_id = Job.make_id(data.get("title", ""), data.get("company", ""), url)
    _app_repo.upsert(job_id, status=status, platform=platform,
                     notes="Reported by Chrome extension")
    return jsonify({"recorded": True, "job_id": job_id}), 200

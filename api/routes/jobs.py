"""api/routes/jobs.py — read job listings."""
from flask import Blueprint, jsonify
from database.repositories.job_repo import JobRepository

jobs_bp = Blueprint("jobs", __name__, url_prefix="/jobs")
_repo = JobRepository()


@jobs_bp.get("/")
def list_jobs():
    return jsonify([j.to_dict() for j in _repo.all()])


@jobs_bp.get("/track/<track>")
def by_track(track):
    return jsonify([j.to_dict() for j in _repo.by_track(track)])

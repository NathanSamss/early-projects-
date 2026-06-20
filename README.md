# Resume Auto-Apply System

A service-oriented job application automation platform. Discovers jobs across
three tracks (security, AI, edge), scores them, tailors a resume and cover
letter with Claude Opus 4.8, and applies through platform-specific adapters.

## Architecture

```
api/          Flask web API — trigger and monitor the pipeline
services/     Business logic (discovery, matching, tailoring, analytics, ...)
adapters/     One per ATS (Greenhouse, Lever, Workday, Ashby) behind a shared interface
workers/      Four-stage RQ pipeline: scrape -> match -> tailor -> apply
database/     SQLAlchemy models + repositories (SQLite now, Postgres-ready)
dashboard/    Streamlit UI
infrastructure/  Docker, scripts, monitoring
```

## The pipeline

Each worker hands off to the next via a Redis queue:

1. **scrape_worker** discovers jobs, enqueues each to match
2. **match_worker** classifies into a track and scores 0-10, enqueues good matches to tailor
3. **tailor_worker** generates summary + cover letter, enqueues to apply
4. **apply_worker** routes to the right adapter and applies (or flags for manual finish)

## Tracks

Jobs are classified into one of three tracks, each scored against its own
keywords, and tailored with track-specific framing:

- **security** — SOC, threat, incident response, SIEM
- **ai** — ML, data science, MLOps, model training
- **edge** — embedded AI, TinyML, robotics, computer vision

## Quick start (Docker)

```bash
cp .env.example .env          # fill in ANTHROPIC_API_KEY and Gmail app password
python infrastructure/scripts/init_resume.py
docker compose up --build
```

Then:

```bash
curl -X POST http://localhost:8000/pipeline/run     # trigger the pipeline
open http://localhost:8501                          # dashboard
```

## Quick start (local, no Docker)

```bash
pip install -r requirements.txt
playwright install chromium
# Start Redis separately (brew install redis && redis-server)
python infrastructure/scripts/init_resume.py
flask --app api.main run --port 8000     # terminal 1
rq worker scrape_queue match_queue tailor_queue apply_queue   # terminal 2
python infrastructure/scripts/trigger_pipeline.py   # terminal 3
```

## Tests

```bash
pytest tests/ -v
```

## Safety

Adapters never auto-submit by default (`APPLY_SETTINGS["auto_submit"] = False`).
They fill the form and flag the application for human review. CAPTCHAs and
multi-step Workday flows are always handed off to a human.

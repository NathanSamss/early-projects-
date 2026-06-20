"""
config.py
Central configuration loaded from environment variables.
Everything tunable lives here so no other module hardcodes values.
"""

import os


# ── DATABASE ──────────────────────────────────────────────────────────────────
# SQLite to start. Swap DATABASE_URL to a postgresql:// string later and
# nothing else in the codebase has to change — SQLAlchemy handles the rest.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/autoapply.db")

# ── REDIS / QUEUES ────────────────────────────────────────────────────────────
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

QUEUE_NAMES = {
    "scrape": "scrape_queue",
    "match":  "match_queue",
    "tailor": "tailor_queue",
    "apply":  "apply_queue",
}

# ── APPLICANT ─────────────────────────────────────────────────────────────────
APPLICANT = {
    "name":  os.getenv("APPLICANT_NAME", ""),
    "email": os.getenv("APPLICANT_EMAIL", ""),
    "phone": os.getenv("APPLICANT_PHONE", ""),
    "linkedin": os.getenv("APPLICANT_LINKEDIN", ""),
    "github":   os.getenv("APPLICANT_GITHUB", ""),
}

# ── AI MODEL ──────────────────────────────────────────────────────────────────
AI_SETTINGS = {
    "model":                 "claude-opus-4-8",
    "max_tokens":            2048,
    "temperature":           0.7,
    "max_description_chars": 4000,
    "max_resume_chars":      4000,
}

# ── APPLICATION BEHAVIOR ──────────────────────────────────────────────────────
APPLY_SETTINGS = {
    "min_match_score":         5,
    "daily_application_limit": 20,
    "delay_between_apps":      30,
    "auto_submit":             False,   # never auto-submit by default; human reviews
}

# ── NETWORK ───────────────────────────────────────────────────────────────────
NETWORK = {
    "request_timeout":   15,
    "scrape_delay":       1.5,
    "max_retry_attempts": 3,
    "retry_delay":        5,
}

# ── PATHS ─────────────────────────────────────────────────────────────────────
RESUME_JSON_PATH = os.getenv("RESUME_JSON_PATH", "data/resume/base_resume.json")
RESUME_PDF_PATH  = os.getenv("RESUME_PDF_PATH",  "data/resume/resume.pdf")
SCREENSHOTS_DIR  = "logs/screenshots"
SESSIONS_DIR     = "data/sessions"
LOG_FILE         = "logs/autoapply.log"

# ── SMTP ──────────────────────────────────────────────────────────────────────
SMTP = {
    "host":     os.getenv("SMTP_HOST", "smtp.gmail.com"),
    "port":     int(os.getenv("SMTP_PORT", "587")),
    "user":     os.getenv("APPLICANT_EMAIL", ""),
    "password": os.getenv("APPLICANT_EMAIL_PASSWORD", ""),
}

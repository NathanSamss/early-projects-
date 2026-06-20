"""
database/models/base.py
SQLAlchemy foundation: declarative Base, engine, and session factory.
Import Base in every model. Import get_session() wherever you need DB access.
"""

import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from config import DATABASE_URL

log = logging.getLogger(__name__)

# Ensure the data directory exists for SQLite
if DATABASE_URL.startswith("sqlite:///"):
    db_path = DATABASE_URL.replace("sqlite:///", "")
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

# check_same_thread is a SQLite-only concern; harmless to pass for others is not,
# so guard it.
_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=_connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False, future=True)

Base = declarative_base()


def get_session() -> Session:
    """Return a new database session. Caller is responsible for closing it."""
    return SessionLocal()


def init_db() -> None:
    """Create all tables. Safe to call repeatedly — only creates what's missing."""
    # Import models so they register with Base before create_all
    from database.models import job, application, match, tailored  # noqa: F401
    Base.metadata.create_all(bind=engine)
    log.info("Database initialized")

"""
services/discovery/base.py
Shared interface and HTTP helpers for all job source scrapers.
"""

import logging
from typing import List, Dict, Any, ClassVar

log = logging.getLogger(__name__)


class BaseSource:
    """A job source returns a list of raw job dicts via fetch()."""

    HEADERS: ClassVar[Dict[str, str]] = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json",
    }

    name: str = "base"

    def fetch(self, keyword: str) -> List[Dict[str, Any]]:
        """Override. Return a list of raw job dicts with normalized keys:
        title, company, location, description, url, source, salary, posted_date."""
        raise NotImplementedError

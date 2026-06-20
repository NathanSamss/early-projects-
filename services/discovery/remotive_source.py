"""
services/discovery/remotive_source.py
Remotive public API — free, no key. Remote tech roles.
Covers software, devops, security, and data categories.
"""

import time
import logging
from typing import List, Dict, Any

import requests

from services.discovery.base import BaseSource
from config import NETWORK

log = logging.getLogger(__name__)


class RemotiveSource(BaseSource):
    name = "remotive"
    BASE_URL = "https://remotive.com/api/remote-jobs"
    CATEGORIES = ["software-dev", "devops-sysadmin", "data"]

    def fetch(self, keyword: str) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        seen: set = set()
        for category in self.CATEGORIES:
            params = {"category": category, "search": keyword, "limit": 50}
            try:
                r = requests.get(self.BASE_URL, params=params,
                                 headers=self.HEADERS, timeout=NETWORK["request_timeout"])
                r.raise_for_status()
                data = r.json()
            except requests.exceptions.RequestException as e:
                log.warning(f"[remotive] {category} error: {e}")
                time.sleep(NETWORK["scrape_delay"])
                continue
            except ValueError as e:
                log.error(f"[remotive] bad JSON {category}: {e}")
                continue

            for item in data.get("jobs", []):
                url = item.get("url", "")
                if url in seen:
                    continue
                seen.add(url)
                out.append({
                    "title": item.get("title", ""),
                    "company": item.get("company_name", ""),
                    "location": "Remote",
                    "description": item.get("description", ""),
                    "url": url,
                    "source": "remotive",
                    "salary": item.get("salary"),
                    "posted_date": item.get("publication_date"),
                })
            log.info(f"[remotive] {keyword}/{category}: {len(data.get('jobs', []))}")
            time.sleep(NETWORK["scrape_delay"])
        return out

"""
services/discovery/jobicy_source.py
Jobicy public API — free, no key. Remote tech roles.

Uses the valid industry names from Jobicy's API (dev, engineering,
data-science, technical-support). The tag parameter is optional: Jobicy
rejects some single-word tags with HTTP 400, so if a tagged request fails
we retry the same industry without a tag rather than losing those jobs.
"""

import time
import logging
from typing import List, Dict, Any

import requests

from services.discovery.base import BaseSource
from config import NETWORK

log = logging.getLogger(__name__)


class JobicySource(BaseSource):
    name = "jobicy"
    BASE_URL = "https://jobicy.com/api/v2/remote-jobs"
    INDUSTRIES = ["dev", "engineering", "data-science", "technical-support"]

    def _request(self, params: Dict[str, Any]):
        return requests.get(self.BASE_URL, params=params,
                            headers=self.HEADERS, timeout=NETWORK["request_timeout"])

    def fetch(self, keyword: str) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        seen: set = set()
        tag = keyword.split()[-1].lower()

        for industry in self.INDUSTRIES:
            data = None
            # First try with the tag; if Jobicy rejects it, retry without a tag.
            for params in ({"count": 50, "industry": industry, "tag": tag},
                           {"count": 50, "industry": industry}):
                try:
                    r = self._request(params)
                    if r.status_code == 400:
                        # invalid tag — fall through to the no-tag attempt
                        continue
                    r.raise_for_status()
                    data = r.json()
                    break
                except requests.exceptions.RequestException as e:
                    log.warning(f"[jobicy] {industry} error: {e}")
                    time.sleep(NETWORK["scrape_delay"])
                except ValueError as e:
                    log.error(f"[jobicy] bad JSON {industry}: {e}")
                    break

            if not data:
                time.sleep(NETWORK["scrape_delay"])
                continue

            for item in data.get("jobs", []):
                url = item.get("url", "")
                if url in seen:
                    continue
                seen.add(url)
                sal_min = item.get("salaryMin")
                sal_max = item.get("salaryMax")
                salary = f"{sal_min} - {sal_max}" if sal_min else None
                out.append({
                    "title": item.get("jobTitle", ""),
                    "company": item.get("companyName", ""),
                    "location": item.get("jobGeo", "Remote"),
                    "description": item.get("jobExcerpt", "") + " " + item.get("jobDescription", ""),
                    "url": url,
                    "source": "jobicy",
                    "salary": salary,
                    "posted_date": item.get("pubDate"),
                })
            log.info(f"[jobicy] {industry}: {len(data.get('jobs', []))} jobs")
            time.sleep(NETWORK["scrape_delay"])
        return out

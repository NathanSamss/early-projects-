"""adapters/workday/workday_adapter.py — Workday ATS (always manual finish)."""
import logging
from typing import Dict, Any
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout, Error as PWError
from adapters.base.base_adapter import BaseAdapter, ApplyResult

log = logging.getLogger(__name__)


class WorkdayAdapter(BaseAdapter):
    platform = "workday"

    def matches(self, url: str) -> bool:
        u = url.lower()
        return "workday.com" in u or "myworkdayjobs.com" in u

    def apply(self, job: Dict[str, Any], profile: Dict[str, str], resume_path: str) -> ApplyResult:
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True, args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage", "--no-sandbox"])
                page = browser.new_context(viewport={"width": 1280, "height": 800}).new_page()
                page.goto(job["url"], timeout=30000)
                page.wait_for_load_state("networkidle", timeout=15000)
                self._human_delay()
                btn = page.query_selector("[data-automation-id=applyButton]")
                if btn:
                    btn.click()
                    page.wait_for_load_state("networkidle", timeout=10000)
                name = profile.get("name", "").split()
                self._fill(page, "[data-automation-id=legalNameSection_firstName]", name[0] if name else "")
                self._fill(page, "[data-automation-id=legalNameSection_lastName]", name[-1] if len(name) > 1 else "")
                self._fill(page, "[data-automation-id=email]", profile.get("email", ""))
                self._fill(page, "[data-automation-id=phone-number]", profile.get("phone", ""))
                self._upload(page, resume_path)
                browser.close()
                # Workday is multi-step and varies per company — always manual finish
                return ApplyResult(False, True, self.platform, "Pre-filled — multi-step, finish manually")
        except (PWTimeout, PWError) as e:
            log.error(f"[workday] {e}")
        return ApplyResult(False, True, self.platform, "Error")

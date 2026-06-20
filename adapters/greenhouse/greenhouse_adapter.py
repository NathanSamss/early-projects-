"""adapters/greenhouse/greenhouse_adapter.py — Greenhouse ATS."""
import logging
from typing import Dict, Any
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout, Error as PWError
from adapters.base.base_adapter import BaseAdapter, ApplyResult
from config import APPLY_SETTINGS

log = logging.getLogger(__name__)


class GreenhouseAdapter(BaseAdapter):
    platform = "greenhouse"

    def matches(self, url: str) -> bool:
        return "greenhouse.io" in url.lower()

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
                name = profile.get("name", "").split()
                self._fill(page, "#first_name", name[0] if name else "")
                self._fill(page, "#last_name", name[-1] if len(name) > 1 else "")
                self._fill(page, "#email", profile.get("email", ""))
                self._fill(page, "#phone", profile.get("phone", ""))
                self._upload(page, resume_path)
                if self._detect_captcha(page):
                    browser.close()
                    return ApplyResult(False, True, self.platform, "CAPTCHA — finish manually")
                if not APPLY_SETTINGS["auto_submit"]:
                    browser.close()
                    return ApplyResult(False, True, self.platform, "Filled — review and submit")
                submit = page.query_selector("input[type=submit], button[type=submit]")
                if submit:
                    submit.click()
                    page.wait_for_load_state("networkidle", timeout=10000)
                    browser.close()
                    return ApplyResult(True, False, self.platform, "Submitted")
                browser.close()
                return ApplyResult(False, True, self.platform, "No submit button")
        except (PWTimeout, PWError) as e:
            log.error(f"[greenhouse] {e}")
        return ApplyResult(False, True, self.platform, "Error")

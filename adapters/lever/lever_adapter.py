"""adapters/lever/lever_adapter.py — Lever ATS."""
import logging
from typing import Dict, Any
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout, Error as PWError
from adapters.base.base_adapter import BaseAdapter, ApplyResult
from config import APPLY_SETTINGS

log = logging.getLogger(__name__)


class LeverAdapter(BaseAdapter):
    platform = "lever"

    def matches(self, url: str) -> bool:
        return "lever.co" in url.lower()

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
                btn = page.query_selector("a[href*=apply], .template-btn-submit")
                if btn:
                    btn.click()
                    page.wait_for_load_state("networkidle", timeout=10000)
                    self._human_delay()
                self._fill(page, "input[name=name]", profile.get("name", ""))
                self._fill(page, "input[name=email]", profile.get("email", ""))
                self._fill(page, "input[name=phone]", profile.get("phone", ""))
                self._upload(page, resume_path)
                if self._detect_captcha(page):
                    browser.close()
                    return ApplyResult(False, True, self.platform, "CAPTCHA — finish manually")
                if not APPLY_SETTINGS["auto_submit"]:
                    browser.close()
                    return ApplyResult(False, True, self.platform, "Filled — review and submit")
                submit = page.query_selector("button[type=submit]")
                if submit:
                    submit.click()
                    page.wait_for_load_state("networkidle", timeout=10000)
                    browser.close()
                    return ApplyResult(True, False, self.platform, "Submitted")
                browser.close()
                return ApplyResult(False, True, self.platform, "No submit button")
        except (PWTimeout, PWError) as e:
            log.error(f"[lever] {e}")
        return ApplyResult(False, True, self.platform, "Error")

"""
adapters/base/base_adapter.py
Common interface every platform adapter implements.

The contract is deliberately small:
  matches(url)  -> bool   : does this adapter handle that URL?
  apply(job, profile) -> ApplyResult : attempt the application

Adapters never auto-submit by default. They fill the form and return a
result telling the caller whether a human needs to finish (CAPTCHA, Workday
multi-step, etc.). This keeps the risky final click under human control.
"""

import os
import time
import random
import logging
from dataclasses import dataclass
from typing import Dict, Any, Optional

log = logging.getLogger(__name__)


@dataclass
class ApplyResult:
    submitted: bool          # True only if fully submitted automatically
    needs_manual: bool       # True if a human must finish
    platform: str
    note: str = ""


class BaseAdapter:
    platform: str = "base"

    def matches(self, url: str) -> bool:
        """Return True if this adapter handles the given URL."""
        raise NotImplementedError

    def apply(self, job: Dict[str, Any], profile: Dict[str, str],
              resume_path: str) -> ApplyResult:
        """Attempt the application. Override in each adapter."""
        raise NotImplementedError

    # ── Shared Playwright helpers ─────────────────────────────────────────────

    def _human_delay(self, lo: float = 0.4, hi: float = 1.2) -> None:
        time.sleep(random.uniform(lo, hi))

    def _fill(self, page, selector: str, value: str) -> bool:
        if not value:
            return False
        try:
            el = page.wait_for_selector(selector, timeout=3000, state="visible")
            if el:
                el.click()
                self._human_delay(0.1, 0.3)
                el.fill(value)
                return True
        except Exception as e:
            log.debug(f"[{self.platform}] fill miss {selector}: {e}")
        return False

    def _upload(self, page, resume_path: str) -> bool:
        if not resume_path or not os.path.exists(resume_path):
            return False
        try:
            fi = page.wait_for_selector("input[type=file]", timeout=5000)
            if fi:
                fi.set_input_files(resume_path)
                self._human_delay(0.5, 1.0)
                return True
        except Exception:
            pass
        return False

    def _detect_captcha(self, page) -> bool:
        try:
            text = page.inner_text("body").lower()
        except Exception:
            return False
        signals = ["click on the icons", "i am not a robot",
                   "human verification", "identical"]
        if any(s in text for s in signals):
            return True
        for sel in ("iframe[src*='recaptcha']", "iframe[src*='hcaptcha']",
                    ".g-recaptcha", "[data-sitekey]"):
            try:
                if page.query_selector(sel):
                    return True
            except Exception:
                pass
        return False

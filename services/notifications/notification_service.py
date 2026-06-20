"""
services/notifications/notification_service.py
Sends a daily summary email via SMTP. Degrades quietly if creds are missing.
"""

import smtplib
import logging
from email.mime.text import MIMEText
from typing import Dict, Any
from config import SMTP

log = logging.getLogger(__name__)


class NotificationService:
    def send_summary(self, summary: Dict[str, Any]) -> None:
        if not SMTP["user"] or not SMTP["password"]:
            log.warning("[notify] SMTP creds missing — skipping summary")
            return

        by_status = summary.get("by_status", {})
        by_track = summary.get("by_track", {})
        body = ["Auto-Apply Daily Summary", "=" * 40,
                f"Total applications: {summary.get('total_applications', 0)}", "",
                "By status:"]
        for k, v in by_status.items():
            body.append(f"  {k}: {v}")
        body.append("")
        body.append("By track:")
        for k, v in by_track.items():
            body.append(f"  {k}: {v}")

        msg = MIMEText("\n".join(body), "plain")
        msg["From"] = SMTP["user"]
        msg["To"] = SMTP["user"]
        msg["Subject"] = "Auto-Apply Daily Summary"

        try:
            with smtplib.SMTP(SMTP["host"], SMTP["port"]) as server:
                server.starttls()
                server.login(SMTP["user"], SMTP["password"])
                server.send_message(msg)
            log.info("[notify] summary sent")
        except smtplib.SMTPAuthenticationError:
            log.error("[notify] SMTP auth failed")
        except Exception as e:
            log.error(f"[notify] error: {e}")

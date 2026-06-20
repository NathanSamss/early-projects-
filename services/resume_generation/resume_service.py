"""
services/resume_generation/resume_service.py
Loads the base resume JSON and merges in tailored content to produce the
final resume text used in an application. PDF generation is a later step;
for now this assembles the tailored text version.
"""

import json
import logging
from typing import Dict, Any
from config import RESUME_JSON_PATH

log = logging.getLogger(__name__)


class ResumeService:
    def load_base(self) -> Dict[str, Any]:
        try:
            with open(RESUME_JSON_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            log.error(f"[resume] base resume not found: {RESUME_JSON_PATH}")
            return {}
        except json.JSONDecodeError as e:
            log.error(f"[resume] invalid JSON: {e}")
            return {}

    def assemble(self, base_resume: Dict[str, Any], tailored_summary: str) -> str:
        """Produce a plain-text resume with the tailored summary at the top."""
        lines = []
        lines.append(base_resume.get("name", ""))
        contact = " | ".join(filter(None, [
            base_resume.get("email", ""),
            base_resume.get("phone", ""),
            base_resume.get("location", ""),
        ]))
        if contact:
            lines.append(contact)
        lines.append("")
        if tailored_summary:
            lines.append("SUMMARY")
            lines.append(tailored_summary)
            lines.append("")
        for exp in base_resume.get("experience", []):
            lines.append(f"{exp.get('title','')} — {exp.get('company','')} ({exp.get('dates','')})")
            for b in exp.get("bullets", []):
                lines.append(f"  - {b}")
            lines.append("")
        return "\n".join(lines)

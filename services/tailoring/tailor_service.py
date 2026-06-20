"""
services/tailoring/tailor_service.py
Generates a tailored summary and cover letter for a job using Claude Opus 4.8.
The system prompt adapts to the job's track so a robotics role gets framed
around embedded/ML experience and a security role around security experience.
"""

import json
import logging
from typing import Dict, Any, Tuple, Optional

import anthropic

from config import AI_SETTINGS

log = logging.getLogger(__name__)
_client: Optional[anthropic.Anthropic] = None

TRACK_FRAMING = {
    "security": "Emphasize security operations, incident response, endpoint protection, "
                "and any SOC, networking, or compliance experience.",
    "ai":       "Emphasize Python, machine learning, model development, data analysis, "
                "and the candidate's AI graduate study.",
    "edge":     "Emphasize embedded systems, on-device inference, hardware, robotics, "
                "computer vision, and any low-level or systems experience.",
}


def _client_get() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic()
    return _client


def _truncate(text: str, limit: int) -> str:
    return text[:limit] if text else ""


def _call(system: str, user: str) -> str:
    try:
        msg = _client_get().messages.create(
            model=AI_SETTINGS["model"],
            max_tokens=AI_SETTINGS["max_tokens"],
            temperature=AI_SETTINGS["temperature"],
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return "".join(b.text for b in msg.content if hasattr(b, "text")).strip()
    except anthropic.AuthenticationError:
        log.error("[tailor] invalid ANTHROPIC_API_KEY")
    except anthropic.RateLimitError:
        log.warning("[tailor] rate limited")
    except anthropic.APIConnectionError:
        log.error("[tailor] cannot reach API")
    except Exception as e:
        log.error(f"[tailor] error: {e}")
    return ""


class TailorService:
    def tailor(self, job: Dict[str, Any], track: str,
               base_resume: Dict[str, Any]) -> Tuple[str, str]:
        framing = TRACK_FRAMING.get(track, "")
        resume_text = _truncate(json.dumps(base_resume, indent=2),
                                AI_SETTINGS["max_resume_chars"])
        job_desc = _truncate(job.get("description", ""),
                             AI_SETTINGS["max_description_chars"])

        summary = _call(
            f"You are an expert technical resume writer. {framing} "
            "Never invent experience. Write concise, specific, achievement-focused content.",
            f"Resume:\n{resume_text}\n\nJob:\nTitle: {job.get('title','')}\n"
            f"Company: {job.get('company','')}\nDescription: {job_desc}\n\n"
            "Write a 2-3 sentence professional summary tailored to this role. "
            "Output only the summary."
        )

        cover = _call(
            f"You are an expert cover letter writer for {track} roles. {framing} "
            "Write a specific, warm, 3-paragraph letter. Never invent qualifications.",
            f"Candidate: {base_resume.get('name','')}\nResume:\n{resume_text}\n\n"
            f"Job:\nTitle: {job.get('title','')}\nCompany: {job.get('company','')}\n"
            f"Description: {job_desc}\n\nWrite a 3-paragraph cover letter. "
            "Output only the letter body."
        )

        return summary, cover

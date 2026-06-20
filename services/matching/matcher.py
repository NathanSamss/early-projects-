"""
services/matching/matcher.py
Classifies a job into a track, then scores it 0-10 against that track's
keyword weights plus overlap with the applicant's resume skills.
"""

import logging
from typing import Dict, Any, Tuple
from services.matching.tracks import TRACKS, classify

log = logging.getLogger(__name__)


def _resume_skills(base_resume: Dict[str, Any]) -> list:
    skills = []
    section = base_resume.get("skills", {})
    if isinstance(section, dict):
        for v in section.values():
            if isinstance(v, list):
                skills.extend(v)
    elif isinstance(section, list):
        skills = section
    return [s.lower() for s in skills if isinstance(s, str)]


def score(job: Dict[str, Any], base_resume: Dict[str, Any]) -> Tuple[str, int]:
    """
    Returns (track, score).
    track is "" and score 0 if the job fits no track.
    """
    text = f"{job.get('title','')} {job.get('description','')}".lower()
    track = classify(text)
    if not track:
        return "", 0

    kw = TRACKS[track]
    points = 0

    # Tool matches (+1 each)
    for tool in kw["tools"]:
        if tool in text:
            points += 1

    # Signal depth (+1 per 2 signal hits)
    signal_hits = sum(1 for s in kw["signals"] if s in text)
    points += signal_hits // 2

    # Entry-level / bonus signals (+2 if any present)
    if any(b in text for b in kw["bonus"]):
        points += 2

    # Remote bonus (+1)
    if "remote" in job.get("location", "").lower():
        points += 1

    # Resume skill overlap (+1 each)
    for skill in _resume_skills(base_resume):
        if skill in text:
            points += 1

    final = min(points, 10)
    log.debug(f"[matcher] {job.get('title','')} -> {track} {final}/10")
    return track, final

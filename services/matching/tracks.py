"""
services/matching/tracks.py
Defines the three role tracks and their scoring keywords.

Each track has:
  - signals:    keywords that classify a job INTO this track
  - tools:      specific technologies worth points when matched
  - bonus:      entry-level and other positive signals

A job is classified into whichever track has the most signal hits.
If no track clears a minimum, the job is dropped.
"""

from typing import Dict, List

TRACKS: Dict[str, Dict[str, List[str]]] = {

    "security": {
        "signals": [
            "security", "soc", "cybersecurity", "infosec", "threat",
            "vulnerability", "penetration", "incident response", "siem",
            "malware", "forensics", "compliance",
        ],
        "tools": [
            "splunk", "wireshark", "nessus", "nmap", "burp suite", "metasploit",
            "crowdstrike", "sentinel", "qradar", "nist", "mitre", "owasp",
            "firewall", "endpoint", "zero trust",
        ],
        "bonus": [
            "entry level", "entry-level", "junior", "associate",
            "tier 1", "soc analyst", "security+", "graduate",
        ],
    },

    "ai": {
        "signals": [
            "machine learning", "ml engineer", "ai engineer", "deep learning",
            "data scientist", "artificial intelligence", "mlops", "nlp",
            "neural network", "model training", "llm",
        ],
        "tools": [
            "pytorch", "tensorflow", "scikit-learn", "keras", "pandas",
            "numpy", "hugging face", "transformers", "mlflow", "kubeflow",
            "python", "sql", "spark",
        ],
        "bonus": [
            "entry level", "entry-level", "junior", "associate", "graduate",
            "new grad", "ml intern", "ai intern",
        ],
    },

    "edge": {
        "signals": [
            "edge ai", "edge ml", "embedded ai", "tinyml", "on-device",
            "edge computing", "embedded systems", "robotics", "computer vision",
            "sensor fusion", "autonomous", "firmware", "iot",
        ],
        "tools": [
            "c++", "embedded c", "raspberry pi", "jetson", "arduino", "ros",
            "opencv", "tensorflow lite", "onnx", "cuda", "fpga", "rtos",
            "edge impulse", "coral",
        ],
        "bonus": [
            "entry level", "entry-level", "junior", "associate", "graduate",
            "new grad", "embedded intern", "robotics intern",
        ],
    },
}


def classify(text: str) -> str:
    """
    Return the track name with the most signal hits in `text`,
    or "" if no track has at least one signal match.
    """
    text = text.lower()
    best_track = ""
    best_hits = 0
    for track_name, kw in TRACKS.items():
        hits = sum(1 for signal in kw["signals"] if signal in text)
        if hits > best_hits:
            best_hits = hits
            best_track = track_name
    return best_track if best_hits >= 1 else ""

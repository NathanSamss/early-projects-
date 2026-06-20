"""Tests for the three-track matcher."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import unittest
from services.matching.tracks import classify
from services.matching.matcher import score

RESUME = {"skills": {"languages": ["python"], "tools": ["servicenow"],
                     "areas": ["machine learning", "endpoint security"]}}


class TestClassify(unittest.TestCase):
    def test_security_job(self):
        self.assertEqual(classify("SOC analyst threat incident response siem"), "security")

    def test_ai_job(self):
        self.assertEqual(classify("machine learning engineer pytorch model training"), "ai")

    def test_edge_job(self):
        self.assertEqual(classify("embedded systems robotics tinyml on-device inference"), "edge")

    def test_unrelated_job(self):
        self.assertEqual(classify("barista coffee customer service"), "")


class TestScore(unittest.TestCase):
    def test_security_scores_in_security_track(self):
        job = {"title": "SOC Analyst", "location": "Remote",
               "description": "splunk siem threat incident nist entry level soc analyst"}
        track, sc = score(job, RESUME)
        self.assertEqual(track, "security")
        self.assertGreaterEqual(sc, 5)

    def test_ai_scores_in_ai_track(self):
        job = {"title": "ML Engineer", "location": "Remote",
               "description": "machine learning pytorch python model training junior"}
        track, sc = score(job, RESUME)
        self.assertEqual(track, "ai")
        self.assertGreaterEqual(sc, 3)

    def test_edge_scores_in_edge_track(self):
        job = {"title": "Embedded AI Engineer", "location": "Remote",
               "description": "embedded systems tinyml jetson c++ ros robotics entry level"}
        track, sc = score(job, RESUME)
        self.assertEqual(track, "edge")
        self.assertGreaterEqual(sc, 3)

    def test_unrelated_returns_empty(self):
        job = {"title": "Barista", "location": "NYC", "description": "make coffee"}
        track, sc = score(job, RESUME)
        self.assertEqual(track, "")
        self.assertEqual(sc, 0)

    def test_score_capped_at_10(self):
        job = {"title": "Senior SOC", "location": "Remote",
               "description": " ".join(["splunk siem nist mitre owasp firewall endpoint "
                                        "threat incident vulnerability soc cybersecurity "
                                        "entry level junior associate"] * 3)}
        track, sc = score(job, RESUME)
        self.assertLessEqual(sc, 10)


if __name__ == "__main__":
    unittest.main(verbosity=2)

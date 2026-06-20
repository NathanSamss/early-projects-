"""Tests for models and repositories using an isolated temp database."""
import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import unittest

# Point the DB at a temp file BEFORE importing anything that builds the engine
_tmpdir = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = f"sqlite:///{_tmpdir}/test.db"

from database.models.base import init_db
from database.repositories.job_repo import JobRepository
from database.repositories.match_repo import MatchRepository
from database.repositories.application_repo import ApplicationRepository
from database.models.application import STATUS_APPLIED


class TestRepositories(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def setUp(self):
        self.jobs = JobRepository()
        self.matches = MatchRepository()
        self.apps = ApplicationRepository()
        self.sample = {"title": "SOC Analyst", "company": "CrowdStrike",
                       "location": "Remote", "description": "security",
                       "url": "https://example.com/1", "source": "test", "track": "security"}

    def test_upsert_returns_id_first_time(self):
        jid = self.jobs.upsert({**self.sample, "url": "https://example.com/unique-first"})
        self.assertIsNotNone(jid)

    def test_upsert_dedupes(self):
        self.jobs.upsert(self.sample)
        second = self.jobs.upsert(self.sample)
        self.assertIsNone(second)

    def test_job_retrievable(self):
        jid = self.jobs.upsert({**self.sample, "url": "https://example.com/2"})
        self.assertTrue(self.jobs.exists(jid))

    def test_match_save_and_get(self):
        jid = self.jobs.upsert({**self.sample, "url": "https://example.com/3"})
        self.matches.save(jid, "security", 7)
        m = self.matches.get(jid)
        self.assertEqual(m.score, 7)
        self.assertEqual(m.track, "security")

    def test_application_status_and_stats(self):
        jid = self.jobs.upsert({**self.sample, "url": "https://example.com/4"})
        self.apps.upsert(jid, track="security", status=STATUS_APPLIED)
        stats = self.apps.stats()
        self.assertGreaterEqual(stats.get(STATUS_APPLIED, 0), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)

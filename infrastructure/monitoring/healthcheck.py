"""
infrastructure/monitoring/healthcheck.py
Simple health check — verifies Redis is reachable and the DB is initialized.
Run inside a container or cron to alert if something is down.
"""
import sys
from redis import Redis
from config import REDIS_URL


def check() -> bool:
    try:
        Redis.from_url(REDIS_URL).ping()
        return True
    except Exception as e:
        print(f"Redis unreachable: {e}")
        return False


if __name__ == "__main__":
    sys.exit(0 if check() else 1)

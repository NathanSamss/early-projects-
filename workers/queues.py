"""
workers/queues.py
RQ queue handles, one per pipeline stage. Workers and the API both import
these so everyone enqueues to the same named queues backed by Redis.
"""
import logging
from redis import Redis
from rq import Queue
from config import REDIS_URL, QUEUE_NAMES

log = logging.getLogger(__name__)

_redis = Redis.from_url(REDIS_URL)

scrape_queue = Queue(QUEUE_NAMES["scrape"], connection=_redis)
match_queue  = Queue(QUEUE_NAMES["match"],  connection=_redis)
tailor_queue = Queue(QUEUE_NAMES["tailor"], connection=_redis)
apply_queue  = Queue(QUEUE_NAMES["apply"],  connection=_redis)

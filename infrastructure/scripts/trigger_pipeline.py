"""
infrastructure/scripts/trigger_pipeline.py
Kick off the pipeline from the command line (or cron) without the API.
Enqueues stage 1; the worker chain handles the rest.
"""
from dotenv import load_dotenv
load_dotenv()

from workers.queues import scrape_queue

if __name__ == "__main__":
    job = scrape_queue.enqueue("workers.scrape_worker.run_discovery")
    print(f"Pipeline triggered — task {job.id}")

"""
api/main.py
Flask application entry point. Wires up routes and initializes the DB.
Run with: flask --app api.main run   (or via gunicorn in Docker)
"""
import logging
from flask import Flask
from database.models.base import init_db
from api.routes.pipeline import pipeline_bp
from api.routes.jobs import jobs_bp
from api.routes.applications import applications_bp

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


def create_app() -> Flask:
    app = Flask(__name__)
    init_db()
    app.register_blueprint(pipeline_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(applications_bp)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)

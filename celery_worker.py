"""Celery worker entry point."""

from backend.app.extensions import celery_app

# Import tasks to register them with Celery
from backend.app.modules.ingestion import tasks  # noqa: F401

if __name__ == '__main__':
    celery_app.start()


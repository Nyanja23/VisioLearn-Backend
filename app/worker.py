"""Celery worker configuration for VisioLearn async tasks"""

import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

# Initialize Celery app
app = Celery(
    'visiolearn',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')
)

# Celery configuration
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes hard limit
    task_soft_time_limit=25 * 60,  # 25 minutes soft limit
    worker_prefetch_multiplier=1,
    worker_pool='solo',  # Windows compatibility: solo pool (sequential, no multiprocessing)
)

# Task routing
app.conf.task_routes = {
    'app.tasks.process_note.process_note_task': {'queue': 'process_notes'},
}

# Register periodic tasks if needed
from celery.schedules import crontab
app.conf.beat_schedule = {
    # Example: check for stale processing tasks daily
    'check-stale-tasks': {
        'task': 'app.tasks.process_note.check_stale_tasks',
        'schedule': crontab(hour=0, minute=0),  # Midnight UTC
    },
}

# Import task modules so Celery can register them
# This MUST happen after app.conf.update() so the configuration is already set
app.autodiscover_tasks(['app.tasks'])

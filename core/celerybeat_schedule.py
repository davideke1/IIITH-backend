
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'fetch_and_store_data_every_30_seconds': {
        'task': 'core.tasks.fetch_and_store_data',
        'schedule': 30.0,  # in seconds
    },
}

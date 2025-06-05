import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('apps')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

schedule = {
    'update_event_statuses': {
        'task': 'apps.events.tasks.update_event_statuses',
        'schedule': crontab(minute=0, hour='*/3'),
    },
}

app.conf.beat_schedule = schedule

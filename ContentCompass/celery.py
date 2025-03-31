from __future__ import absolute_import
import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ContentCompass.settings')

app = Celery('ContentCompass')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all apps
app.autodiscover_tasks()

app.conf.broker_connection_retry_on_startup = True

app.conf.beat_schedule = {
    'daily-subscription-maintenance': {
        'task': 'core.tasks.handle_subscription_lifecycle',
        'schedule': crontab(hour=0, minute=0),
    }
}


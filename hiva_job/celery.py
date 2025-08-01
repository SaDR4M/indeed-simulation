import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hiva_job.settings')

app = Celery('hiva_job')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.conf.worker_pool = 'solo'
app.config_from_object('django.conf:settings', namespace='CELERY')
broker_connection_retry_on_startup = True

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


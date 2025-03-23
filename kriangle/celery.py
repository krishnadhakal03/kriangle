import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kriangle.settings')

app = Celery('kriangle')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# For local development, we'll use Django database as the broker and backend
app.conf.update(
    broker_url='django-db://',
    result_backend='django-db',
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

@app.task(bind=True, name='debug-task')
def debug_task(self):
    print(f'Request: {self.request!r}') 
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "onboarding.settings")
app = Celery("onboarding")
app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.update(
    task_routes={
        'orders.tasks.process_upstream_order': {'queue': 'orders'},
        'utils.tasks.notify_store': {'queue': 'notifications'}
    },
)

app.autodiscover_tasks()

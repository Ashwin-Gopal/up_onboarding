import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "onboarding.settings")
app = Celery("onboarding")
app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.update(
    task_routes={
        'orders.tasks.process_upstream_order': {'queue': 'orders'},
        'utils.tasks.notify_store': {'queue': 'notifications'}
    },
)

app.conf.beat_schedule = {
    'update-inventory-data-redis': {
        'task': 'utils.tasks.push_inventory_data_to_redis',
        'schedule': crontab(hour=23, minute=30, day_of_week='*'),
    },
}
app.autodiscover_tasks()

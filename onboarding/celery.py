import logging
import os

import structlog
from celery import Celery
from celery.schedules import crontab
from celery.signals import setup_logging
from django_structlog.celery.steps import DjangoStructLogInitStep

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "onboarding.settings")
app = Celery("onboarding")
app.config_from_object("django.conf:settings", namespace="CELERY")

app.steps['worker'].add(DjangoStructLogInitStep)

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


# Logging
@setup_logging.connect
def receiver_setup_logging(loglevel, logfile, format, colorize, **kwargs):  # pragma: no cover
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json_formatter": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processor": structlog.processors.JSONRenderer(),
                },
                "plain_console": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processor": structlog.dev.ConsoleRenderer(),
                },
                "key_value": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processor": structlog.processors.KeyValueRenderer(
                        key_order=['timestamp', 'level', 'event', 'logger']),
                },
            },
            "handlers": {
                "json_file": {
                    "class": "logging.handlers.WatchedFileHandler",
                    "filename": "logs/task_json.log",
                    "formatter": "json_formatter",
                },
                "flat_line_file": {
                    "class": "logging.handlers.WatchedFileHandler",
                    "filename": "logs/task_flat_line.log",
                    "formatter": "key_value",
                },
            },
            "loggers": {
                "django_structlog": {
                    "handlers": ["flat_line_file", "json_file"],
                    "level": "INFO",
                },
                "onboarding": {
                    "handlers": ["flat_line_file", "json_file"],
                    "level": "INFO",
                },
            }
        }
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

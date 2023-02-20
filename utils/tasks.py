from celery import shared_task
from celery.utils.log import get_task_logger

from onboarding.celery import app

logger = get_task_logger(__name__)


@app.task
def notify_store(store_id):
    """
    Task to notify store about the order
    :param store_id:
    :return:
    """
    print("Received Order from aggregator")
    logger.info("Notifying Store {}".format(store_id))

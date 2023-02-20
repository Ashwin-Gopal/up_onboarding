from celery import shared_task
from celery.utils.log import get_task_logger

from onboarding.celery import app

logger = get_task_logger(__name__)


@app.task
def process_upstream_order(payload):
    """
    Task to process the orders sent by different aggregators
    :param payload:
    :return:
    """
    print("Received Order from aggregator")
    logger.info("Order Payload", payload)

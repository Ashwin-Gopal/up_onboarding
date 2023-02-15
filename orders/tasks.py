from celery import shared_task

@shared_task()
def process_upstream_order(payload):
    """
    Task to process the orders sent by different aggregators
    :param payload:
    :return:
    """
    print("Received Order from aggregator")
    print(payload)

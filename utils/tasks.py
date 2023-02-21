import json

import redis
from celery.utils.log import get_task_logger

from inventory.models import Aggregator, Store, StoreItemPrice
from onboarding.celery import app

logger = get_task_logger(__name__)

r = redis.Redis()


@app.task
def notify_store(store_id):
    """
    Task to notify store about the order
    :param store_id:
    :return:
    """
    print("Received Order from aggregator")
    logger.info("Notifying Store {}".format(store_id))


@app.task
def push_inventory_data_to_redis():
    aggregators = list(Aggregator.objects.all().values_list('id', flat=True))
    stores = list(Store.objects.all().values_list('id', flat=True))
    inventory_dict = dict()

    for agg in aggregators:
        agg_dict = dict()
        for store in stores:
            store_dict = dict()
            for item in StoreItemPrice.objects.filter(store_id=store, aggregator_id=agg):
                store_dict[item.id] = str(item.price)
            if store_dict:
                agg_dict[store] = store_dict
        if agg_dict:
            inventory_dict[agg] = agg_dict

    r.set('inventory', json.dumps(inventory_dict))
    logger.info("Updated Redis with inventory data")
    print("Updated Redis with inventory data")

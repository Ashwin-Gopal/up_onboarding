import redis
import json

from inventory.models import Aggregator, Store, StoreItemPrice

r = redis.Redis()


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

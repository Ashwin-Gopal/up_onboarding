import uuid
import random
import time
import redis
import json
r = redis.Redis()

inventory = json.loads(r.get('inventory'))

aggregators = list(inventory.keys())


def generate_items(agg_id, store_id):
    """
    Method to generate order items
    :return:
    """
    total_amount = 0
    items = list()
    quantity = random.randint(1, 4)
    i_choices = list(inventory[agg_id][store_id].keys())
    i = random.choices(i_choices)[0]
    price = quantity * float(inventory[agg_id][store_id][i])
    total_amount += price
    items.append(
        {
            "itemId": i,
            "price": price,
            "quantity": quantity
        }
    )
    return items, total_amount


def produce_order():
    """
    form order payload
    :return:
    """
    order = dict()
    order['aggregatorOrderId'] = str(uuid.uuid4())
    agg_id = random.choices(aggregators)[0]
    store_id = random.choices(list(inventory[agg_id].keys()))[0]
    order['aggregatorId'] = agg_id
    order['storeId'] = store_id
    order['timeStamp'] = int(time.time())
    items, total_amount = generate_items(agg_id, store_id)
    order['items'] = items
    order['price'] = total_amount

    return order

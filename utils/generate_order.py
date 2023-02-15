import uuid
import random
import time


def generate_items():
    """
    Method to generate order items
    :return:
    """
    total_amount = 0
    items = list()
    for item in range(random.randint(1, 5)):
        quantity = random.randint(1, 5)

        price = quantity * random.randint(50, 500)
        total_amount += price
        items.append(
            {
                "itemId": random.randint(1, 10000),
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
    order['aggregatorId'] = random.randint(1, 6)
    order['storeId'] = random.randint(1, 100)
    order['timeStamp'] = int(time.time())
    items, total_amount = generate_items()
    order['items'] = items
    order['price'] = total_amount

    return order


# for order in range(random.randint(1, 10)):
#     print(produce_order())

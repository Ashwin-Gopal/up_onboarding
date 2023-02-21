import json
from datetime import datetime

from celery.utils.log import get_task_logger

from onboarding.celery import app
from orders.models import Order, OrderItem

logger = get_task_logger(__name__)


@app.task
def process_upstream_order(payload):
    """
    Task to process the orders sent by different aggregators
    :param payload:
    :return:
    """
    # {'aggregatorOrderId': 'e8f2b990-4102-4fbb-bbe6-bc61372b71d7', 'aggregatorId': '3', 'storeId': '2',
    # 'timeStamp': 1676961496, 'items': [{'itemId': '12', 'price': 300.0, 'quantity': 1}], 'price': 300.0}
    try:
        obj = Order.objects.create(
            aggregator_id=payload.get('aggregatorId'),
            store_id=payload.get('storeId'),
            amount=payload.get('price'),
            aggregator_order_id=payload.get('aggregatorOrderId'),
            order_placed=datetime.fromtimestamp(payload.get('timeStamp'))
        )
        order_items = [
            OrderItem(
                order=obj,
                item_id=item.get('itemId'),
                add_on=item.get('addOn', False),
                quantity=item.get('quantity')
            )
            for item in payload.get('items')
        ]

        OrderItem.objects.bulk_create(order_items)
    except Exception as e:
        print(e)
        logger.error("Processing Order failed with agg {agg_id} and agg_order {agg_order_id}".format(
            agg_id=payload.get('aggregatorId'), agg_order_id=payload.get('aggregatorOrderId')))

    logger.info("Order Payload : {order}".format(order=json.dumps(payload)))

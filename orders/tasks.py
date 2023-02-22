import json
from datetime import datetime

from celery.utils.log import get_task_logger
from django.db import transaction

from onboarding.celery import app
from orders.models import Order, OrderItem
from utils.tasks import notify_store

logger = get_task_logger('onboarding')


@app.task
@transaction.atomic
def process_upstream_order(payload):
    """
    Task to process the orders sent by different aggregators
    :param payload:
    :return:
    """
    save_point = transaction.savepoint()
    system_order_id = -99
    try:
        obj = Order.objects.create(
            aggregator_id=payload.get('aggregatorId'),
            store_id=payload.get('storeId'),
            amount=payload.get('price'),
            aggregator_order_id=payload.get('aggregatorOrderId'),
            order_placed=datetime.fromtimestamp(payload.get('timeStamp'))
        )
        system_order_id = obj.id
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
        logger.error(
            "Task Id: {task_id}. Processing Order failed with agg {agg_id} and agg_order {agg_order_id}.".format(
                agg_id=payload.get('aggregatorId'), agg_order_id=payload.get('aggregatorOrderId'),
                task_id=process_upstream_order.request.id))
        transaction.savepoint_rollback(save_point)

    logger.info("Notifying Store about order {id}".format(id=payload.get('aggregatorOrderId')))

    notify_store.delay(payload.get('storeId'))

    logger.info("Task Id: {task_id}. Order processed : {order}".format(
        order=json.dumps({
            'agg': payload.get('aggregatorId'),
            'agg_order': payload.get('aggregatorOrderId'),
            'system_order': system_order_id}),
        task_id=process_upstream_order.request.id
    )
    )

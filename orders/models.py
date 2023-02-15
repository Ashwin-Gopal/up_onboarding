from django.db import models

from inventory.models import StoreItemPrice, Store, Aggregator


class CustomDateTime(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Order(CustomDateTime):
    aggregator = models.ForeignKey(Aggregator, on_delete=models.SET_NULL, null=True)
    store = models.ForeignKey(Store, on_delete=models.SET_NULL, related_name='orders', null=True)
    amount = models.FloatField()
    aggregator_order_id = models.CharField(max_length=100, unique=True)
    order_placed = models.DateTimeField(null=True)

    class Meta:
        db_table = 'order'
        unique_together = ('aggregator', 'aggregator_order_id',)


class OrderItem(models.Model):
    item = models.ForeignKey(StoreItemPrice, on_delete=models.SET_NULL, null=True)
    add_on = models.BooleanField(default=False)
    quantity = models.IntegerField()
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')

    class Meta:
        db_table = 'orderItem'

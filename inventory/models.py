from django.db import models

from django.conf import settings

from users.models import Role


class CustomDateTime(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


def get_super_admin():
    """
    Method to get super admin
    :return:
    """
    return Role.objects.filter(name='superAdmin').user_set.all().first()


class Merchant(CustomDateTime):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET(get_super_admin), )

    class Meta:
        db_table = 'merchant'


class Aggregator(CustomDateTime):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'aggregator'


class Store(CustomDateTime):
    name = models.CharField(max_length=250)
    address = models.TextField(blank=True, null=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6)
    lng = models.DecimalField(max_digits=9, decimal_places=6)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name='stores')

    class Meta:
        db_table = 'store'


class ItemCategory(CustomDateTime):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'itemCategory'


class Item(CustomDateTime):
    name = models.CharField(max_length=50)

    class Meta:
        db_table = 'item'


class StoreItemPrice(CustomDateTime):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='price')
    description = models.TextField()
    aggregator = models.ForeignKey(Aggregator, on_delete=models.CASCADE, related_name='items_price')
    price = models.DecimalField(max_digits=9, decimal_places=2)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='items_price')
    categories = models.ManyToManyField(ItemCategory)

    class Meta:
        db_table = 'storeItemPrice'

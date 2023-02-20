from tastypie import fields
from tastypie.resources import ModelResource
from inventory.models import Merchant, ItemCategory, Store, Item, Aggregator, StoreItemPrice
from tastypie.authorization import Authorization
from tastypie.constants import ALL
from users.api.resources import OnboardingUserResource
from utils.authentication import TokenAuthentication
from utils.authorization import MerchantAuthorization, StoreAuthorization


class MerchantResource(ModelResource):

    user = fields.ForeignKey(OnboardingUserResource, 'user')

    class Meta:
        queryset = Merchant.objects.all()
        resource_name = 'merchants'
        allowed_methods = ['get', 'post', 'patch', 'delete']
        authentication = TokenAuthentication()
        authorization = MerchantAuthorization()
        get_excludes = ('created_on', 'updated_on')


class StoreResource(ModelResource):

    merchant = fields.IntegerField(attribute='merchant_id')

    class Meta:
        queryset = Store.objects.all()
        resource_name = 'stores'
        allowed_methods = ['get', 'post', 'patch', 'delete']
        authentication = TokenAuthentication()
        authorization = StoreAuthorization()
        filtering = {
            "name": ALL,
        }


class ItemCategoryResource(ModelResource):

    class Meta:
        queryset = ItemCategory.objects.all()
        resource_name = 'item-categories'
        allowed_methods = ['get', 'post', 'patch', 'delete']
        authorization = Authorization()
        authentication = TokenAuthentication()

    def dehydrate_name(self, bundle):
        """
        Method to convert name to Title format
        :param bundle:
        :return:
        """
        return bundle.data['name'].title()


class ItemResource(ModelResource):

    class Meta:
        queryset = Item.objects.all()
        resource_name = 'items'
        allowed_methods = ['get', 'post', 'patch', 'delete']
        authorization = Authorization()
        authentication = TokenAuthentication()


class AggregatorResource(ModelResource):

    class Meta:
        queryset = Aggregator.objects.all()
        resource_name = 'aggregators'
        allowed_methods = ['get', 'post', 'patch', 'delete']
        authorization = Authorization()
        authentication = TokenAuthentication()


class StoreItemPriceResource(ModelResource):

    aggregator = fields.ForeignKey(AggregatorResource, 'aggregator')
    item = fields.ForeignKey(ItemResource, 'item')
    store = fields.ForeignKey(StoreResource, 'store')
    categories = fields.ManyToManyField(ItemCategoryResource, 'categories')

    class Meta:
        queryset = StoreItemPrice.objects.all()
        resource_name = 'store-item-prices'
        allowed_methods = ['get', 'post', 'patch', 'delete']
        authorization = Authorization()
        authentication = TokenAuthentication()

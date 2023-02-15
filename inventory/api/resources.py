from tastypie.resources import ModelResource
from inventory.models import Merchant, ItemCategory
from tastypie.authorization import Authorization


class MerchantResource(ModelResource):

    class Meta:
        queryset = Merchant.objects.all()
        resource_name = 'merchants'
        allowed_methods = ['get', 'post', 'patch', 'delete']
        authorization = Authorization()


class ItemCategoryResource(ModelResource):

    class Meta:
        queryset = ItemCategory.objects.all()
        resource_name = 'item-categories'
        allowed_methods = ['get', 'post', 'patch', 'delete']
        authorization = Authorization()

    def dehydrate_name(self, bundle):
        """
        Method to convert name to Title format
        :param bundle:
        :return:
        """
        return bundle.data['name'].title()

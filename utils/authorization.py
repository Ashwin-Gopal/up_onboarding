import json

import ipdb
from tastypie.authorization import Authorization, DjangoAuthorization
from tastypie.exceptions import Unauthorized
from django.contrib.auth.models import Group

from inventory.models import Merchant, Store


def has_permission(code_name, request):
    """
    check whether user has permission
    :param code_name:
    :param request:
    :return:
    """
    request_user_role = request.user.role

    group = Group.objects.get(name=request_user_role.name)

    # now we check here for specific permission
    if code_name not in group.permissions.all().values_list('codename', flat=True):
        raise Unauthorized("You are not allowed to access that resource.")

    return True


class MerchantAuthorization(DjangoAuthorization):

    def create_detail(self, object_list, bundle):
        """
        Permission to check if user can add merchant
        :param object_list:
        :param bundle:
        :return:
        """
        return has_permission('add_merchant', bundle.request)

    def read_list(self, object_list, bundle):
        """
        Method to return the Model object list.
        :param object_list:
        :param bundle:
        :return:
        """
        return object_list

    def read_detail(self, object_list, bundle):
        """
        Permission to check if user has view merchant details
        :param object_list:
        :param bundle:
        :return:
        """
        return has_permission('view_merchant', bundle.request)

    def delete_list(self, object_list, bundle):
        """
        Permission to check if user can delete merchant list
        :param object_list:
        :param bundle:
        :return:
        """
        has_permission('edit_merchant', bundle.request)
        return object_list

    def delete_detail(self, object_list, bundle):
        """
        Permission to check if user can delete merchant
        :param object_list:
        :param bundle:
        :return:
        """
        return has_permission('edit_merchant', bundle.request)

    def update_detail(self, object_list, bundle):
        """
        Permission to check if user can update merchant
        :param object_list:
        :param bundle:
        :return:
        """
        return has_permission('edit_merchant', bundle.request)


class StoreAuthorization(DjangoAuthorization):

    def create_detail(self, object_list, bundle):
        """
        Permission to check if user can add store
        :param object_list:
        :param bundle:
        :return:
        """
        return has_permission('add_store', bundle.request)

    def read_list(self, object_list, bundle):
        """
        Method to return the Model object list.
        :param object_list:
        :param bundle:
        :return:
        """
        return object_list

    def read_detail(self, object_list, bundle):
        """
        Permission to check if user has view store details
        :param object_list:
        :param bundle:
        :return:
        """
        return has_permission('view_store', bundle.request)

    def delete_list(self, object_list, bundle):
        """
        Permission to check if user can delete store list
        :param object_list:
        :param bundle:
        :return:
        """
        has_permission('edit_store', bundle.request)
        return object_list

    def delete_detail(self, object_list, bundle):
        """
        Permission to check if user can delete store
        :param object_list:
        :param bundle:
        :return:
        """
        return has_permission('edit_store', bundle.request)

    def update_detail(self, object_list, bundle):
        """
        Permission to check if user can delete store
        :param object_list:
        :param bundle:
        :return:
        """
        return has_permission('edit_store', bundle.request) and self.check_owner(bundle.request)

    @staticmethod
    def check_owner(request):
        """
        Method to check owner
        :param request:
        :return:
        """
        full_path = request.get_full_path()
        store_id = full_path.split('/api/v1/stores/')[1].split('/')[0]
        request_user = request.user
        store = Store.objects.filter(id=store_id).select_related('merchant', 'merchant__user').first()
        store_owner = store.merchant.user
        return store_owner == request_user

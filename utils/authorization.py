from django.contrib.auth.models import Group
from tastypie.authorization import DjangoAuthorization
from tastypie.exceptions import Unauthorized

from inventory.models import Store


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
    if not group.permissions.filter(codename=code_name).exists():
        raise Unauthorized("You are not allowed to access that resource.")

    return True


class BasePermissionAuthorization(DjangoAuthorization):

    def __init__(self, create_permission, list_permission, detail_permission, edit_permission):
        self.create = create_permission
        self.list = list_permission
        self.detail = detail_permission
        self.edit = edit_permission

    def create_detail(self, object_list, bundle):
        """
        Permission to check if user can add object
        :param object_list:
        :param bundle:
        :return:
        """
        return has_permission(self.create, bundle.request)

    def read_list(self, object_list, bundle):
        """
        Method to return the Model object list.
        :param object_list:
        :param bundle:
        :return:
        """
        return object_list if has_permission(self.list, bundle.request) else object_list.none()

    def read_detail(self, object_list, bundle):
        """
        Permission to check if user has view object details
        :param object_list:
        :param bundle:
        :return:
        """
        return has_permission(self.detail, bundle.request)

    def delete_list(self, object_list, bundle):
        """
        Permission to check if user can delete object list
        :param object_list:
        :param bundle:
        :return:
        """
        return object_list if has_permission(self.edit, bundle.request) else object_list.none()

    def delete_detail(self, object_list, bundle):
        """
        Permission to check if user can delete object
        :param object_list:
        :param bundle:
        :return:
        """
        return has_permission(self.edit, bundle.request)

    def update_detail(self, object_list, bundle):
        """
        Permission to check if user can update object
        :param object_list:
        :param bundle:
        :return:
        """
        return has_permission(self.edit, bundle.request)

    def update_list(self, object_list, bundle):
        """
        Permission to check if user can update object list
        :param object_list:
        :param bundle:
        :return:
        """
        return object_list if has_permission(self.edit, bundle.request) else object_list.none()


class StoreAuthorization(BasePermissionAuthorization):

    def update_detail(self, object_list, bundle):
        """
        Permission to check if user can update store
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

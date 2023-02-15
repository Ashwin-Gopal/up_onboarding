from tastypie.authentication import Authentication

from users.models import UserToken
from datetime import datetime


class TokenAuthentication(Authentication):
    def is_authenticated(self, request, **kwargs):
        """
        method to authenticate the user
        :param request:
        :param kwargs:
        :return:
        """
        authenticated = False
        token = request.META.get('HTTP_AUTHORIZATION')
        if token:
            authenticated = UserToken.objects.filter(token=token, expire_at__gte=datetime.now().date()).exists()
        return authenticated

    def get_identifier(self, request):
        """
        method to get identifier
        :param request:
        :return:
        """
        return request.user.username

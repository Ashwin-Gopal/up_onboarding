from tastypie.authentication import ApiKeyAuthentication

from users.models import UserToken
from datetime import datetime


class TokenAuthentication(ApiKeyAuthentication):
    def is_authenticated(self, request, **kwargs):
        """
        method to authenticate the user
        :param request:
        :param kwargs:
        :return:
        """
        authenticated = super(TokenAuthentication, self).is_authenticated(request, **kwargs)

        token = request.META.get('HTTP_AUTHORIZATION')
        if token:
            user_token = UserToken.objects.filter(token=token, expire_at__gte=datetime.now().date())
            authenticated = user_token.exists()
            request.user = user_token.first().user if authenticated else None
        return authenticated

    def get_identifier(self, request):
        """
        method to get identifier
        :param request:
        :return:
        """
        return request.user.username

from django.contrib.auth import authenticate
from django.urls import path
from silk.profiling.profiler import silk_profile
from tastypie import fields
from tastypie.exceptions import BadRequest
from tastypie.http import HttpUnauthorized
from tastypie.resources import ModelResource
from datetime import datetime, timedelta
from users.constants import RequestKeys, ResponseKeys, ErrorMessages
from users.models import Role, OnboardingUser, UserToken
from tastypie.authorization import Authorization

from utils.authentication import TokenAuthentication


class RoleResource(ModelResource):

    class Meta:
        queryset = Role.objects.all()
        resource_name = 'roles'
        allowed_methods = ['get', 'post', 'patch', 'delete']
        authorization = Authorization()


class OnboardingUserResource(ModelResource):

    role = fields.ForeignKey(RoleResource, 'role')
    signup_required_fields = ("username", "firstName", "email", "password")
    login_required_fields = ("username", "password")

    class Meta:
        queryset = OnboardingUser.objects.all()
        resource_name = 'onboarding-users'
        fields = ['id', 'first_name', 'username']
        allowed_methods = ['get', 'patch', 'delete']
        authorization = Authorization()
        authentication = TokenAuthentication()

    def prepend_urls(self):
        """
        aggregator order processing urls
        :return:
        """
        return [
            path("onboarding-users/signup/", self.wrap_view('sign_up'), name='create-user'),
            path("onboarding-users/login/", self.wrap_view('login'), name='login-user'),
            path("onboarding-users/logout/", self.wrap_view('logout'), name='logout-user'),
        ]

    def get_token(self, user):
        """
        Method to fetch session token
        :param user:
        :return:
        """
        token_obj = UserToken.objects.filter(user=user, expire_at__gte=datetime.now().date()).first()
        if not token_obj:
            UserToken.objects.filter(user=user).delete()
            token_obj = UserToken.objects.create(user=user, expire_at=datetime.now().date() + timedelta(days=7))
        return token_obj.token

    def sign_up(self, request, **kwargs):
        """
        Method to create user entry
        :param request:
        :param kwargs:
        :return:
        """
        self.method_check(request, allowed=['post'])
        data = self.deserialize(request, request.body, format=request.META.get(
            'CONTENT_TYPE', 'application/json'))
        username = data.get(RequestKeys.USERNAME)
        email = data.get(RequestKeys.EMAIL)
        password = data.get(RequestKeys.PASSWORD)
        role = data.get(RequestKeys.ROLE)
        first_name = data.get(RequestKeys.FIRST_NAME)

        missing_fields = set(self.signup_required_fields).difference(set(data.keys()))
        if missing_fields:
            raise BadRequest(ErrorMessages.MISSING_FIELDS.format(missing_fields))

        user, create = OnboardingUser.objects.get_or_create(username=username, defaults={"first_name": first_name,
                                                                                         "password": password,
                                                                                         "email": email})
        if not create:
            raise BadRequest(ErrorMessages.DUPLICATE_USER)
        user.set_password(password)
        user.role = Role.objects.get(id=role)
        user.save()
        token = self.get_token(user)

        return self.create_response(request, {
            ResponseKeys.SESSION_TOKEN: token,
            ResponseKeys.ID: user.id
        })

    @silk_profile()
    def login(self, request, **kwargs):
        """
        Method to log in the user
        :param request:
        :param kwargs:
        :return:
        """
        self.method_check(request, allowed=['post'])
        data = self.deserialize(request, request.body, format=request.META.get(
            'CONTENT_TYPE', 'application/json'))
        username = data.get(RequestKeys.USERNAME)
        password = data.get(RequestKeys.PASSWORD)

        missing_fields = set(self.login_required_fields).difference(set(data.keys()))
        if missing_fields:
            raise BadRequest(ErrorMessages.MISSING_FIELDS.format(missing_fields))

        user = authenticate(username=username, password=password)
        if user:
            token = self.get_token(user)
            return self.create_response(request, {
                ResponseKeys.SESSION_TOKEN: token,
                ResponseKeys.USER_INFO: {
                    ResponseKeys.EMAIL: user.email,
                    ResponseKeys.USERNAME: user.username,
                    ResponseKeys.FIRST_NAME: user.first_name
                }
            })
        else:
            return self.create_response(
                request,
                {ResponseKeys.MESSAGE: ErrorMessages.LOGIN_ERROR},
                HttpUnauthorized
            )

    def logout(self, request, **kwargs):
        """
        Method to log out the user
        :param request:
        :param kwargs:
        :return:
        """
        self.method_check(request, allowed=['delete'])
        self.is_authenticated(request)
        token = request.META.get('HTTP_AUTHORIZATION')

        UserToken.objects.filter(token=token).delete()

        return self.create_response(request, {
            ResponseKeys.SUCCESS: True
        })




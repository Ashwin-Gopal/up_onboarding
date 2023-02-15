"""onboarding URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, re_path, include
from tastypie.api import Api

from orders.api.resources import OrderResource
from users.api.resources import OnboardingUserResource, RoleResource
from inventory.api.resources import MerchantResource, ItemCategoryResource

v1_api = Api(api_name='v1')
v1_api.register(OnboardingUserResource())
v1_api.register(RoleResource())
v1_api.register(MerchantResource())
v1_api.register(ItemCategoryResource())
v1_api.register(OrderResource())


urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^api/', include(v1_api.urls)),
]

if settings.DEBUG:
    urlpatterns += [path('silk/', include('silk.urls', namespace='silk'))]

from django.contrib import admin
from users.models import Role, OnboardingUser
# Register your models here.


admin.site.register(Role)
admin.site.register(OnboardingUser)

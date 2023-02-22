import hmac
import uuid
from hashlib import sha1
from datetime import datetime, timedelta
from django.contrib.auth.models import AbstractUser
from django.db import models


def create_user_token(sender, instance, created, **kwargs):
    """
    Method to create User Token when new user is created.
    :param sender:
    :param instance:
    :param created:
    :param kwargs:
    :return:
    """
    if kwargs.get('raw', False) is False and created is True:
        UserToken.objects.create(user=instance, expire_at=datetime.now() + timedelta(days=7))


class CustomDateTime(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Role(CustomDateTime):
    ROLE_CHOICES = (
        ('superAdmin', 'Super Admin'),
        ('merchantOwner', 'Merchant Owner'),
        ('user', 'User'),
    )

    name = models.CharField(max_length=50, choices=ROLE_CHOICES,)

    class Meta:
        db_table = 'role'


class OnboardingUser(AbstractUser):
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        db_table = 'onboardinguser'


models.signals.post_save.connect(create_user_token, sender=OnboardingUser)


class UserToken(CustomDateTime):
    user = models.ForeignKey(OnboardingUser, on_delete=models.CASCADE, unique=True, db_index=True)
    token = models.CharField(max_length=128, blank=True, default='', db_index=True)
    expire_at = models.DateField(default=datetime.now().date() + timedelta(days=7))

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_token()

        return super(UserToken, self).save(*args, **kwargs)

    @staticmethod
    def generate_token():
        """
        Method to generate token
        :return:
        """
        new_uuid = uuid.uuid4()
        return hmac.new(new_uuid.bytes, digestmod=sha1).hexdigest()

from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from tastypie.test import ResourceTestCaseMixin
from inventory.models import ItemCategory, Merchant
from users.models import OnboardingUser, Role

CustomPermissionSet = {
    'superAdmin': [
        {
            "name": "Can view merchant",
            "codename": "view_merchant"
        },
        {
            "name": "Can add merchant",
            "codename": "add_merchant"
        },
        {
            "name": "Can edit merchant",
            "codename": "edit_merchant"
        },
        {
            "name": "Can list merchants",
            "codename": "list_merchants"
        }
    ],
    'merchantOwner': [
        {
            "name": "Can view merchant",
            "codename": "view_merchant"
        },
        {
            "name": "Can list merchants",
            "codename": "list_merchants"
        }
    ],
    'user': [
        {
            "name": "Can view merchant",
            "codename": "view_merchant"
        },
        {
            "name": "Can list merchants",
            "codename": "list_merchants"
        }
    ]
}


def migrate_group_permission():
    content_type_object = ContentType.objects.get_for_model(OnboardingUser)
    role_objects = Role.objects.all()
    for each_role_object in role_objects:
        group_object, created = Group.objects.get_or_create(name=each_role_object.name)
        for each_permission in CustomPermissionSet.get(group_object.name, []):
            permission_obj = Permission.objects.filter(
                codename=each_permission['codename'],
                name=each_permission['name']
            ).first()
            if not permission_obj:
                permission_obj = Permission.objects.create(
                    codename=each_permission['codename'],
                    name=each_permission['name'],
                    content_type=content_type_object
                )
            group_object.permissions.add(permission_obj)


class ItemCategoryResourceTest(ResourceTestCaseMixin, TestCase):

    def setUp(self):
        super(ItemCategoryResourceTest, self).setUp()

        self.username = 'test_case_admin_user'
        self.password = 'test_case_password'
        self.user = OnboardingUser.objects.create_user(self.username, 'test_user@test.com', self.password)
        self.user.role = Role.objects.get(name='superAdmin')
        self.user.save()
        self.user_token = self.user.usertoken_set.all().first().token

        ItemCategory.objects.create(
            name='Test Category'
        )

        self.item_category_1 = ItemCategory.objects.get(name='Test Category')

        self.detail_url = '/api/v1/item-categories/{0}/'.format(self.item_category_1.pk)

        self.post_data = {
            "name": "Test Category - Duplicate"
        }

    def test_get_list_json(self):
        resp = self.api_client.get('/api/v1/item-categories/', format='json', authentication=self.user_token)
        self.assertValidJSONResponse(resp)

        self.assertEqual(self.deserialize(resp)['objects'][0]['id'], self.item_category_1.pk)
        self.assertEqual(self.deserialize(resp)['objects'][0]['name'], 'Test Category')
        self.assertEqual(self.deserialize(resp)['objects'][0]['resource_uri'],
                         '/api/v1/item-categories/{0}/'.format(self.item_category_1.pk))

    def test_get_detail_json(self):
        resp = self.api_client.get(self.detail_url, format='json', authentication=self.user_token)
        self.assertValidJSONResponse(resp)

        self.assertKeys(self.deserialize(resp), ['created_on', 'id', 'name', 'resource_uri', 'updated_on'])
        self.assertEqual(self.deserialize(resp)['name'], 'Test Category')

    def test_post_list(self):
        self.assertEqual(ItemCategory.objects.count(), 1)
        self.assertHttpCreated(self.api_client.post('/api/v1/item-categories/', format='json', data=self.post_data,
                                                    authentication=self.user_token))
        self.assertEqual(ItemCategory.objects.count(), 2)

    def test_patch_detail(self):
        original_data = self.deserialize(self.api_client.get(self.detail_url, format='json',
                                                             authentication=self.user_token))
        new_data = original_data.copy()
        new_data['name'] = 'Updated: Test Category'

        self.assertEqual(ItemCategory.objects.count(), 1)
        self.assertHttpAccepted(self.api_client.patch(self.detail_url, format='json', data=new_data,
                                                      authentication=self.user_token))
        self.assertEqual(ItemCategory.objects.count(), 1)

    def test_delete_detail(self):
        self.assertEqual(ItemCategory.objects.count(), 1)
        self.assertHttpAccepted(self.api_client.delete(self.detail_url, format='json', authentication=self.user_token))
        self.assertEqual(ItemCategory.objects.count(), 0)


class MerchantResourceTest(ResourceTestCaseMixin, TestCase):

    def setUp(self):
        super(MerchantResourceTest, self).setUp()

        self.sa_username = 'test_sa_case_admin_user'
        self.normal_username = 'test_normal_user'
        self.merchant_username = 'test_merchant_user'
        self.password = 'test_case_password'

        self.sa_user = OnboardingUser.objects.create_user(self.sa_username, 'test_sa_user@test.com', self.password)
        self.sa_user.role = Role.objects.get(name='superAdmin')
        self.sa_user.save()
        self.sa_user_token = self.sa_user.usertoken_set.all().first().token

        self.normal_user = OnboardingUser.objects.create_user(self.normal_username, 'test_normal_user@test.com',
                                                              self.password)
        self.normal_user.role = Role.objects.get(name='user')
        self.normal_user.save()
        self.normal_user_token = self.normal_user.usertoken_set.all().first().token

        self.merchant_user = OnboardingUser.objects.create_user(self.merchant_username, 'test_merchant_user@test.com',
                                                                self.password)
        self.merchant_user.role = Role.objects.get(name='merchantOwner')
        self.merchant_user.save()
        self.merchant_user_token = self.merchant_user.usertoken_set.all().first().token

        Merchant.objects.create(
            name='Test Merchant',
            user=self.merchant_user
        )

        self.merchant_1 = Merchant.objects.get(name='Test Merchant')

        self.detail_url = '/api/v1/merchants/{0}/'.format(self.merchant_1.pk)

        self.post_data = {
            "name": "Test Merchant - Duplicate",
            "user": '/api/v1/onboarding-users/{0}/'.format(self.merchant_user.pk)
        }
        migrate_group_permission()

    def test_get_list_json(self):
        for token in [self.sa_user_token, self.merchant_user_token, self.normal_user_token]:
            resp = self.api_client.get('/api/v1/merchants/', format='json', authentication=token)
            self.assertValidJSONResponse(resp)

            self.assertEqual(self.deserialize(resp)['objects'][0]['id'], self.merchant_1.pk)
            self.assertEqual(self.deserialize(resp)['objects'][0]['name'], 'Test Merchant')
            self.assertEqual(self.deserialize(resp)['objects'][0]['resource_uri'],
                             '/api/v1/merchants/{0}/'.format(self.merchant_1.pk))
            self.assertEqual(self.deserialize(resp)['objects'][0]['user'],
                             '/api/v1/onboarding-users/{0}/'.format(self.merchant_user.pk))

    def test_get_detail_json(self):
        for token in [self.sa_user_token, self.merchant_user_token, self.normal_user_token]:
            resp = self.api_client.get(self.detail_url, format='json', authentication=token)

            self.assertValidJSONResponse(resp)
            self.assertKeys(self.deserialize(resp), ['created_on', 'id', 'name', 'resource_uri', 'updated_on', 'user'])
            self.assertEqual(self.deserialize(resp)['name'], 'Test Merchant')
            self.assertEqual(self.deserialize(resp)['user'],
                             '/api/v1/onboarding-users/{0}/'.format(self.merchant_user.pk))

    def test_post_list(self):
        self.assertEqual(Merchant.objects.count(), 1)
        self.assertHttpCreated(self.api_client.post('/api/v1/merchants/', format='json', data=self.post_data,
                                                    authentication=self.sa_user_token))
        self.assertEqual(Merchant.objects.count(), 2)

        # Merchant Owner and Normal User should not be able to create merchants
        for token in [self.merchant_user_token, self.normal_user_token]:
            self.assertHttpUnauthorized(self.api_client.post('/api/v1/merchants/', format='json', data=self.post_data,
                                                             authentication=token))
            self.assertEqual(Merchant.objects.count(), 2)

    def test_patch_detail(self):
        original_data = self.deserialize(self.api_client.get(self.detail_url, format='json',
                                                             authentication=self.sa_user_token))
        new_data = original_data.copy()
        new_data['name'] = 'Updated: Test Merchant'

        self.assertEqual(Merchant.objects.count(), 1)
        self.assertHttpAccepted(self.api_client.patch(self.detail_url, format='json', data=new_data,
                                                      authentication=self.sa_user_token))
        self.assertEqual(Merchant.objects.count(), 1)

        # Merchant Owner and Normal User should not be able to edit merchants
        for token in [self.merchant_user_token, self.normal_user_token]:
            self.assertHttpUnauthorized(self.api_client.patch(self.detail_url, format='json', data=new_data,
                                                              authentication=token))

    def test_delete_detail(self):
        # Merchant Owner and Normal User should not be able to delete merchants
        for token in [self.merchant_user_token, self.normal_user_token]:
            self.assertHttpUnauthorized(self.api_client.delete(self.detail_url, format='json', authentication=token))

        self.assertEqual(Merchant.objects.count(), 1)
        self.assertHttpAccepted(
            self.api_client.delete(self.detail_url, format='json', authentication=self.sa_user_token))
        self.assertEqual(Merchant.objects.count(), 0)

from django.test import TestCase
from tastypie.test import ResourceTestCaseMixin
from inventory.models import ItemCategory


class ItemCategoryResourceTest(ResourceTestCaseMixin, TestCase):

    def setUp(self):
        super(ItemCategoryResourceTest, self).setUp()

        ItemCategory.objects.create(
            name='Test Category'
        )

        self.item_category_1 = ItemCategory.objects.get(name='Test Category')

        self.detail_url = '/api/v1/item-categories/{0}/'.format(self.item_category_1.pk)

        self.post_data = {
            "name": "Test Category - Duplicate"
        }

    def test_get_list_json(self):
        resp = self.api_client.get('/api/v1/item-categories/', format='json')
        self.assertValidJSONResponse(resp)

        self.assertEqual(self.deserialize(resp)['objects'][0]['id'], self.item_category_1.pk)
        self.assertEqual(self.deserialize(resp)['objects'][0]['name'], 'Test Category')
        self.assertEqual(self.deserialize(resp)['objects'][0]['resource_uri'],
                         '/api/v1/item-categories/{0}/'.format(self.item_category_1.pk))

    def test_get_detail_json(self):
        resp = self.api_client.get(self.detail_url, format='json')
        self.assertValidJSONResponse(resp)

        self.assertKeys(self.deserialize(resp), ['created_on', 'id', 'name', 'resource_uri', 'updated_on'])
        self.assertEqual(self.deserialize(resp)['name'], 'Test Category')

    def test_post_list(self):
        self.assertEqual(ItemCategory.objects.count(), 1)
        self.assertHttpCreated(self.api_client.post('/api/v1/item-categories/', format='json', data=self.post_data))
        self.assertEqual(ItemCategory.objects.count(), 2)

    def test_patch_detail(self):
        original_data = self.deserialize(self.api_client.get(self.detail_url, format='json'))
        new_data = original_data.copy()
        new_data['name'] = 'Updated: Test Category'

        self.assertEqual(ItemCategory.objects.count(), 1)
        self.assertHttpAccepted(self.api_client.patch(self.detail_url, format='json', data=new_data))
        self.assertEqual(ItemCategory.objects.count(), 1)

    def test_delete_detail(self):
        self.assertEqual(ItemCategory.objects.count(), 1)
        self.assertHttpAccepted(self.api_client.delete(self.detail_url, format='json'))
        self.assertEqual(ItemCategory.objects.count(), 0)

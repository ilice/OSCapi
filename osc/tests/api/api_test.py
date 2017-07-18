from django.test import TestCase


class ParcelAPITest(TestCase):
    base_url = '/api/parcels/'

    def test_get_parcel_returns_json_200(self):
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')

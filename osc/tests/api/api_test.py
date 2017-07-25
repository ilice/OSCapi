from django.test import TestCase
import json
from jsonschema import validate
from nose.plugins.attrib import attr


class ParcelAPITest(TestCase):

    parcel_schema_file = 'osc/tests/api/fixtures/parcel_schema.json'

    with open(parcel_schema_file) as data_file:
        parcel_schema = json.load(data_file)

    def test_get_parcels_returns_json_200(self):
        url = '/parcels/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')

    @attr('elastic_connection')
    def test_get_parcels_by_cadastral_code_returns_valid_parcel(self):
        cadastralCode = "37284A00600114"
        url = '/parcels/{}/'
        response = self.client.get(url.format(cadastralCode))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')
        self.assertIsNone(validate(json.loads(response.content.decode('utf8')),
                          self.parcel_schema))

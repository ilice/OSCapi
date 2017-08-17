from django.test import TestCase
import json
from jsonschema import validate
import mock
from nose.plugins.attrib import attr


class APITest(TestCase):
    base_url = '/'

    def test_get_returns_json_200(self):
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')

    def test_get_returns_browsable_api(self):
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')
        self.assertEqual(
            json.loads(response.content.decode('utf8')),
            {
                "userParcels": "http://testserver/userParcel/",
                "userparcel": "http://testserver/userparcel/query/",
                "auth-signIn": "http://testserver/auth-signIn",
                "user-url": "http://testserver/user/",
                "userparcel_add": "http://testserver/userparcel/add/",
                "crops": "http://testserver/crops/elastic/search/",
                "altitude": "http://testserver/altitud/",
                "api-root": "http://testserver/",
                "owned-parcels": "http://testserver/owned-parcels/",
                "cadastral_parcel": "http://testserver/cadastral/parcel/",
                "parcels": "http://testserver/parcels/"
            }
        )


class ParcelAPITest(TestCase):

    parcel_schema_file = 'osc/tests/api/fixtures/parcel_schema.json'
    parcel_document_by_nationalCadastralReference_response_file = 'osc/tests/api/fixtures/get_parcel_document_by_nationalCadastralReference_response.json'
    parcel_by_nationalCadastralReference_response_file = 'osc/tests/api/fixtures/get_parcel_by_nationalCadastralReference_response.json'

    with open(parcel_document_by_nationalCadastralReference_response_file) as parcel_document_data_file:
        parcel_document_by_nationalCadastralReference_response = json.load(parcel_document_data_file)

    with open(parcel_by_nationalCadastralReference_response_file) as parcel_data_file:
        parcel_by_nationalCadastralReference_response = json.load(parcel_data_file)

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

    @mock.patch('osc.util.parser.es.search', return_value=parcel_document_by_nationalCadastralReference_response)
    def test_get_parcels_by_cadastral_code_calls_elastic(self, mock_es):
        cadastralCode = "37284A00600114"
        url = '/parcels/{}/'
        self.client.get(url.format(cadastralCode))
        mock_es.assert_called_with(body={'query': {'match': {'properties.nationalCadastralReference': cadastralCode}}}, doc_type='parcel', index='parcels')

    @mock.patch('osc.util.parser.es.search', return_value=parcel_document_by_nationalCadastralReference_response)
    def test_get_parcels_by_cadastral_code_returns_correct_parcel(self, mock_es):
        self.maxDiff = None
        cadastralCode = "37284A00600114"
        url = '/parcels/{}/'
        response = self.client.get(url.format(cadastralCode))
        self.assertEqual(response.data, self.parcel_by_nationalCadastralReference_response)

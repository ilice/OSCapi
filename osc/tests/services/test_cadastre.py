# coding=utf-8

from django.test import TestCase, tag
from unittest import skip
import json
import mock
from django.conf import settings

import osc.importer.cadastre as impcadastre
import osc.services.cadastre as cadastre
from osc.exceptions import CadastreException


# This method will be used by the mock to replace requests.get
def mocked_requests(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code
            if status_code == 200:
                self.ok = True
            else:
                self.ok = False
            self.text = json.dumps(json_data)

        def json(self):
            return self.json_data
    if args[0] == 'http://ovc.catastro.meh.es/INSPIRE/wfsCP.aspx':
        return MockResponse({"key1": "value1"}, 200)

    return MockResponse(None, 404)


class CadastreServiceTest(TestCase):

    fixtures_file = 'osc/tests/services/fixtures/cadastre_fixtures.json'

    with open(fixtures_file) as data_file:
        cadastre_fixture = json.load(data_file)

    cadastralParcel = cadastre_fixture['cadastralParcel']

    def setUp(self):
        pass

    @mock.patch('osc.services.cadastre.requests.get',
                side_effect=mocked_requests)
    @mock.patch('osc.services.cadastre.parse_inspire_response')
    def test_call_inspire_when_get_inspire_data(self,
                                                mock_parse,
                                                mock_request_get):
        mock_parse.return_value = []
        cadastre.get_inspire_data_by_code('11015A01400009')
        mock_request_get.assert_called_with(
            settings.CADASTRE['url_inspire'],
            params={'service': 'wfs',
                    'request': 'getfeature',
                    'STOREDQUERIE_ID': 'GetParcel',
                    'srsname': settings.CADASTRE['zone.for.queries'],
                    'REFCAT': '11015A01400009'})

    @mock.patch('osc.services.cadastre.requests.get',
                side_effect=mocked_requests)
    @mock.patch('osc.services.cadastre.parse_inspire_response', '')
    @mock.patch('osc.services.cadastre.url_inspire',
                'http://ovc.catastro.meh.es/INSPIRE/bad_url.aspx')
    def test_raise_exception_when_inspire_data_return_404(self,
                                                          mock_request_get):
        self.assertRaises(CadastreException,
                          cadastre.get_inspire_data_by_code,
                          '11015A01400009')

    def test_get_inspire_data_from_inspire_source(self):
        parcels = cadastre.get_inspire_data_by_code('11015A01400009')
        self.assertTrue(len(parcels) == 1, "should obtain one and only one "
                        "parcel for a cadastral reference")
        self.maxDiff = None
        self.assertDictEqual(self.cadastralParcel, parcels[0])

    def test_public_cadastre_info(self):
        cadastre.get_public_cadastre_info('40167A00805001')

    @skip("Very very long test")
    @tag('elastic_connection')
    def test_update_cadastral_information(self):
        impcadastre.update_cadastral_information()

    @tag('elastic_connection')
    def test_create_mapping(self):
        cadastre.create_parcel_mapping()

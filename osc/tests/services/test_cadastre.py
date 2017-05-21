# coding=utf-8

from django.test import TestCase
from nose.plugins.attrib import attr
from unittest import skip
import json
import mock
from django.conf import settings
import xml.etree.ElementTree as ET

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
    elif args[0] == 'http://ovc.catastro.meh.es/ovcservweb/' \
                    'OVCSWLocalizacionRC/OVCCallejero.asmx/Consulta_DNPRC':
        return MockResponse({"key2": "value2"}, 200)

    return MockResponse(None, 404)


class InspireServiceTest(TestCase):
    fixtures_file = 'osc/tests/services/fixtures/cadastre_fixtures.json'

    with open(fixtures_file) as data_file:
        cadastre_fixture = json.load(data_file)

    inspireError = cadastre_fixture['inspireError']

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
        self.assertTrue("geometry" in parcels[0],
                        "returns geometry for the parcel")

    def test_parse_inspire_response_when_inspire_returns_error(
            self):
        self.assertRaises(CadastreException,
                          cadastre.parse_inspire_response,
                          self.inspireError)


class CadastreServiceTest(TestCase):
    fixtures_file = 'osc/tests/services/fixtures/cadastre_fixtures.json'

    with open(fixtures_file) as data_file:
        cadastre_fixture = json.load(data_file)

    cadastreError = cadastre_fixture['cadastreError']

    @mock.patch('osc.services.cadastre.requests.get',
                side_effect=mocked_requests)
    @mock.patch('osc.services.cadastre.parse_inspire_response')
    def test_call_cadastre_when_public_cadastre_info(self,
                                                     mock_parse,
                                                     mock_request_get):
        mock_parse.return_value = []
        code = '40167A00805001'
        cadastre.get_public_cadastre_info(code)
        mock_request_get.assert_called_with(
            settings.CADASTRE['cadastral_info_url'],
            params={'Provincia': '',
                    'Municipio': '',
                    'RC': code})

    @mock.patch('osc.services.cadastre.requests.get',
                side_effect=mocked_requests)
    @mock.patch('osc.services.cadastre.parse_inspire_response', '')
    @mock.patch('osc.services.cadastre.url_public_cadastral_info',
                'http://ovc.catastro.meh.es/ovcservweb/' +
                'OVCSWLocalizacionRC/OVCCallejero.asmx/bad_url')
    def test_dont_raise_exception_even_when_cadastre_returns_404(
            self,
            mock_request_get):
        code = '40167A00805001'
        cadastre.get_public_cadastre_info(code)
        # The test runner will catch all exceptions you didn't assert
        # would be raised, assert_(True) do nothing but ensures that didn't
        # forget an assertion
        self.assert_(True)

    def test_get_cadastre_data_from_cadastre_source(self):
        parcels = cadastre.get_public_cadastre_info('11015A01400009')
        self.assertTrue(parcels['control']['cudnp'] == 1, "should obtain one "
                        "and only one parcel data for a cadastral reference")

    def test_parse_public_cadastre_response_when_cadastre_returns_error(
            self):
        elem = ET.fromstring(self.cadastreError)
        self.assertRaises(CadastreException,
                          cadastre.parse_public_cadastre_response,
                          elem)

    @skip("Very very long test")
    @attr('elastic_connection')
    def test_update_cadastral_information(self):
        impcadastre.update_cadastral_information()

    @attr('elastic_connection')
    def test_create_mapping(self):
        cadastre.create_parcel_mapping()

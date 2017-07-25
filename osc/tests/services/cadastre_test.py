# coding=utf-8
from django.conf import settings
from django.test import override_settings
from django.test import TestCase
import json
import mock
from nose.plugins.attrib import attr
import xml.etree.ElementTree as ET

from osc.exceptions import CadastreException
import osc.services.cadastre as cadastre

fixtures_file = 'osc/tests/services/fixtures/cadastre_fixtures.json'


with open(fixtures_file) as data_file:
    cadastre_fixture = json.load(data_file)


# This method will be used by the mock to replace requests.get
def mocked_requests(*args, **kwargs):
    class MockResponse(object):
        def __init__(self, json_data='', text='', status_code=404):
            self.json_data = json_data
            self.status_code = status_code
            self.encoding = 'utf-8'
            self.content = text
            if status_code == 200:
                self.ok = True
            else:
                self.ok = False
            self.text = text

        def json(self):
            return self.json_data
    if args[0] == 'http://ovc.catastro.meh.es/INSPIRE/wfsCP.aspx':
        return MockResponse(
            json_data={"key1": "value1"},
            text='<html></html>',
            status_code=200)
    elif args[0] == 'http://ovc.catastro.meh.es/ovcservweb/' \
                    'OVCSWLocalizacionRC/OVCCallejero.asmx/Consulta_DNPRC':
        return MockResponse(
            json_data={"key1": "value1"},
            text='<html></html>',
            status_code=200)
    elif args[0] == 'http://ovc.catastro.meh.es/ovcservweb/' \
                    'OVCSWLocalizacionRC/OVCCallejero.asmx/Consulta_DNPRC/' \
                    'bad_url':
        return MockResponse(
            text='bad_url Web Service method name is not valid.',
            status_code=500)

    return MockResponse(
        text='<html><body>No match mocked get url</body></html>',
        status_code=400)


def mocked_requests_with_bad_response(*args, **kwargs):
    """Will be used to mock requests.get when requested source has problems."""
    class MockResponse(object):
        def __init__(self, html_data, status_code):
            self.status_code = status_code
            if status_code == 200:
                self.ok = True
            else:
                self.ok = False
            self.text = html_data

        def json(self):
            return self.json_data

    if args[0] == 'http://ovc.catastro.meh.es/ovcservweb/' \
                  'OVCSWLocalizacionRC/OVCCallejero.asmx/Consulta_DNPRC':
        return MockResponse(cadastre_fixture['response_400'], 400)

    return MockResponse(None, 404)


def raiseException(e, f):
    raise e


class InspireServiceTest(TestCase):

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
            {'service': 'wfs',
             'request': 'getfeature',
             'STOREDQUERIE_ID': 'GetParcel',
             'srsname': settings.CADASTRE['zone.for.queries'],
             'REFCAT': '11015A01400009'})

    @mock.patch('osc.services.cadastre.requests.get',
                side_effect=mocked_requests)
    @mock.patch('osc.services.cadastre.parse_inspire_response', '')
    @mock.patch('osc.services.cadastre.url_inspire',
                'http://ovc.catastro.meh.es/INSPIRE/bad_url.aspx')
    @override_settings(ERROR_HANDLER=['DBErrorHandler'])
    def test_raise_exception_when_inspire_data_return_404(self,
                                                          mock_request_get):
        self.assertRaises(CadastreException,
                          cadastre.get_inspire_data_by_code,
                          '11015A01400009')

    @attr('cadastre_connection')
    def test_get_inspire_data_from_inspire_source(self):
        parcels = cadastre.get_inspire_data_by_code('11015A01400009')
        self.assertTrue(len(parcels) == 1, "should obtain one and only one "
                        "parcel for a cadastral reference")
        self.assertTrue("geometry" in parcels[0],
                        "returns geometry for the parcel")

    @mock.patch('osc.services.cadastre.error_managed.handle_exception')
    def test_parse_inspire_response_when_inspire_returns_error(
            self, mock_handle_exception):
        mock_handle_exception.side_effect = raiseException
        self.assertRaises(CadastreException,
                          cadastre.parse_inspire_response,
                          self.inspireError)
        mock_handle_exception.assert_called()


class CadastreServiceTest(TestCase):
    fixtures_file = 'osc/tests/services/fixtures/cadastre_fixtures.json'

    with open(fixtures_file) as data_file:
        cadastre_fixture = json.load(data_file)

    cadastreError = cadastre_fixture['cadastreError']
    parcels = cadastre_fixture['parcels']
    scaned_parcels = cadastre_fixture['scanedParcels']

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
    @mock.patch('osc.services.cadastre.url_public_cadastral_info',
                'http://ovc.catastro.meh.es/ovcservweb/'
                'OVCSWLocalizacionRC/OVCCallejero.asmx/Consulta_DNPRC/'
                'bad_url')
    @override_settings(ERROR_HANDLER=['DBErrorHandler'])
    def test_dont_raise_exception_even_when_cadastre_returns_500(
            self,
            mock_request_get):
        code = '40167A00805001'
        cadastre.get_public_cadastre_info(code)
        # The test runner will catch all exceptions you didn't assert
        # would be raised, assertTrue() do nothing but ensures that didn't
        # forget an assertion
        self.assertTrue(True, "shouldn't throw exceptions")

    @attr('cadastre_connection')
    def test_get_cadastre_data_from_cadastre_source(self):
        parcels = cadastre.get_public_cadastre_info('11015A01400009')
        self.assertTrue(parcels['control']['cudnp'] == 1, "should obtain one "
                        "and only one parcel data for a cadastral reference")

    @override_settings(ERROR_HANDLER=['DBErrorHandler'])
    def test_parse_public_cadastre_response_when_cadastre_returns_error(
            self):
        elem = ET.fromstring(self.cadastreError)
        self.assertRaises(CadastreException,
                          cadastre.parse_public_cadastre_response,
                          elem)

    @mock.patch('osc.services.cadastre.get_public_cadastre_info',
                side_effect=mocked_requests)
    def test_call_get_public_cadastre_info_when_add_public_cadastral_info(
            self,
            mock_get_public_cadastre_info):
        cadastre.add_public_cadastral_info(self.parcels)
        for parcel in self.parcels:
            mock_get_public_cadastre_info.assert_any_call(
                parcel['properties']['nationalCadastralReference']
            )
        self.assertTrue(
            mock_get_public_cadastre_info.call_count == len(self.parcels))

    @attr('elastic_connection')
    def test_create_mapping(self):
        cadastre.create_parcel_mapping()

    @mock.patch('osc.services.cadastre.scan')
    def test_scan_parcels(self,
                          m_scan):
        update = mock.Mock()
        m_scan.return_value = self.scaned_parcels['hits']['hits']
        cadastre.scan_parcels(update)
        call_counter = 0
        for parcel in self.scaned_parcels['hits']['hits']:
            call_counter += 1
            update.assert_any_call(
                parcel['_source']['properties']['nationalCadastralReference'])
        self.assertTrue(
            call_counter == len(self.scaned_parcels['hits']['hits']),
            "called once per parcel"
        )

    @attr('elastic_connection')
    def test_get_parcels_by_bbox(self):
        min_lat = 40.440727
        min_lon = -5.758944
        max_lat = 40.440917
        max_lon = -5.757657

        cadastre.get_parcels_by_bbox(min_lat, min_lon, max_lat, max_lon)
        # self.assertTrue(False, 'not implemented yet')

# coding=utf-8

from django.test import TestCase
import json
import mock
from nose.plugins.attrib import attr
from unittest import skip

import osc.importer.cadastre as cadastre


def mock_update_cadastral_province():
    return None


class mocked_feed(object):
    # TODO(teanocrata): teanocrata - fixture returns dict but code accesses
    # entries like attribute and I dont not how to do this without wrapper
    def __init__(self, d):
        self.__dict__ = d


class InspireImporterTest(TestCase):
    fixtures_file = 'osc/tests/importer/fixtures/inspire_fixtures.json'

    with open(fixtures_file) as data_file:
        inspire_fixture = json.load(data_file)

    @skip("Very very long test")
    @attr('elastic_connection')
    def test_update_cadastral_information(self):
        cadastre.update_cadastral_information()

    @mock.patch('osc.importer.cadastre.feedparser')
    @mock.patch('osc.importer.cadastre.update_cadastral_province',
                return_value=None)
    def test_call_inspire_when_get_inspire_data(self,
                                                m_update_cadastral_province,
                                                m_feedparser):
        # TODO(teanocrata): smells, I need help with it
        m_update_cadastral_province.assert_not_called()
        m_feedparser.parse.return_value = mocked_feed(self.inspire_fixture)
        cadastre.update_cadastral_information()
        m_update_cadastral_province.assert_called_once()

    @mock.patch('osc.importer.cadastre.scan_parcels')
    @mock.patch('osc.importer.cadastre.update_parcel_by_cadastral_code')
    def test_update_cadastre_information_scan_parcels_updating_it(
            self,
            m_update_parcel_by_cadastral_code,
            m_scan_parcels):
        cadastre.update_cadastre_information()
        m_scan_parcels.assert_called_once()
        m_scan_parcels.assert_called_with(m_update_parcel_by_cadastral_code)

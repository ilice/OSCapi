from django.test import TestCase
from nose.plugins.attrib import attr
from django.conf import settings
import mock
import json

import osc.services.climate as elastic


class ClimateServiceTest(TestCase):

    fixtures_file = 'osc/tests/services/fixtures/climate_fixtures.json'

    with open(fixtures_file) as data_file:
        climate_fixture = json.load(data_file)

    elastic_closest_station = \
        climate_fixture['closest_station']['elastic']
    api_closest_station = climate_fixture['closest_station']['api']
    query_closest_station = climate_fixture['closest_station']['query']

    elastic_aggregated_measures = \
        climate_fixture['aggregated_measures']['elastic']
    api_aggregated_measures = \
        climate_fixture['aggregated_measures']['api']
    query_aggregated_measures = \
        climate_fixture['aggregated_measures']['query']

    def setUp(self):
        pass

    @mock.patch('osc.services.climate.es')
    def test_call_elastic_when_get_closest_station(self, mock_es):
        elastic.get_closest_station(40.439983, -5.737026)
        mock_es.search.assert_called_with(
            index=settings.INFORIEGO['index'],
            doc_type=settings.INFORIEGO['station.mapping'],
            body=self.query_closest_station)

    @mock.patch('osc.services.climate.es')
    def test_get_closest_station(self, mock_es):
        mock_es.search.return_value = self.elastic_closest_station
        self.assertDictEqual(self.api_closest_station,
                             elastic.get_closest_station(40.439983, -5.737026))

    @attr('elastic_connection')
    def test_get_closest_station_from_elastic(self):

        self.maxDiff = None
        res = elastic.get_closest_station(40.439983, -5.737026)
        # Check some data
        self.assertTrue("LATITUD" in res, "obtain latitude of closest station")
        self.assertTrue("X_UTM" in res, "obtain X_UTM of closest station")
        self.assertTrue("Y_UTM" in res, "obtain Y_UTM of closest station")
        self.assertTrue("FECHAINSTAL" in res,
                        "ontain install date of closest station")
        self.assertTrue("ALTITUD" in res, "obtain altitude of closest station")
        self.assertTrue("IDESTACION" in res, "obtain id of closest station")
        self.assertTrue("lat_lon" in res, "lat_lon of closest station")

    @mock.patch('osc.services.climate.es')
    def test_call_elastic_when_get_aggregated_measures(self, mock_es):
        elastic.get_aggregated_climate_measures('102', '5', 2)
        mock_es.search.assert_called_with(
            index=settings.INFORIEGO['index'],
            doc_type=settings.INFORIEGO['daily.mapping'],
            body=self.query_aggregated_measures)

    @mock.patch('osc.services.climate.es')
    def test_get_aggregated_measures(self, mock_es):
        mock_es.search.return_value = self.elastic_aggregated_measures
        self.maxDiff = None
        self.assertDictEqual(
            self.api_aggregated_measures,
            elastic.get_aggregated_climate_measures('102', '5', 2))

    @attr('elastic_connection')
    def test_get_aggregated_measures_from_elastic(self):
        res = elastic.get_aggregated_climate_measures('102', '5', 2)
        self.maxDiff = None

        self.assertTrue(len(res['by_month']) >= 1,
                        "returns aggregations by month")
        self.assertTrue((res['by_day']),
                        "returns aggregations by day")
        self.assertTrue(type(res['last_year']) == dict,
                        "returns last year aggregations")

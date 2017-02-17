from django.test import TestCase
import osc.services.climate as elastic


class ElasticServiceTest(TestCase):
    def setUp(self):
        pass

    def test_get_closest_station(self):
        elastic.get_closest_station(40.439983, -5.737026)

    def test_get_aggregated_measures(self):
        res = elastic.get_aggregated_climate_measures('102', '5', 3)

        self.assertEqual('', '')
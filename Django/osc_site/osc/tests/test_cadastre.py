from django.test import TestCase
import osc.services.importer.cadastre as cadastre

class BatchProcessServiceTest(TestCase):
    def setUp(self):
        pass

    def test_get_inspire_data(self):
        cadastre.get_inspire_data(436567.6, 4581935.2, 436626.71, 4582031.17)

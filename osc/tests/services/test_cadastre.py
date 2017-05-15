# coding=utf-8

from django.test import TestCase, tag
from unittest import skip

import osc.importer.cadastre as impcadastre
import osc.services.cadastre as cadastre


class CadastreServiceTest(TestCase):
    def setUp(self):
        pass

    def test_get_inspire_data(self):
        parcels = cadastre.get_inspire_data_by_code('11015A01400009')

    def test_public_cadastre_info(self):
        cadastre.get_public_cadastre_info('40167A00805001')

    @skip("Very very long test")
    @tag('elastic_connection')
    def test_update_cadastral_information(self):
        impcadastre.update_cadastral_information()

    @tag('elastic_connection')
    def test_create_mapping(self):
        cadastre.create_parcel_mapping()

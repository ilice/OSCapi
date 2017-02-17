# coding=utf-8

from django.test import TestCase

import osc.importer.cadastre as impcadastre
import osc.services.cadastre as cadastre


class CadastreServiceTest(TestCase):
    def setUp(self):
        pass

    def test_get_inspire_data(self):
        parcels = cadastre.get_inspire_data_by_code('11015A01400009')
        print str(parcels)

    def test_public_cadastre_info(self):
        cadastre.get_public_cadastre_info('40167A00805001')

    def test_update_cadastral_information(self):
        impcadastre.update_cadastral_information()

    def test_create_mapping(self):
        cadastre.create_parcel_mapping()
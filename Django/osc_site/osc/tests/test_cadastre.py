# coding=utf-8

from django.test import TestCase

import osc.services.cadastre as cadastre
import osc.services.importer.cadastre as impcadastre


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

    def test_get_zip_file(self):
        impcadastre.get_parcels_from_url('http://www.catastro.minhap.es/INSPIRE/CadastralParcels/39/39012-CABEZON DE LA SAL/A.ES.SDGC.CP.39012.zip')

    def test_create_mapping(self):
        cadastre.create_parcel_mapping()
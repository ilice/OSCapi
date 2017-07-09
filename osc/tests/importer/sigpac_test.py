# coding=utf-8

from django.test import override_settings
from django.test import TestCase
import mock
import os
from unittest import skip

from osc.exceptions import ItacylException
import osc.importer.sigpac as sigpac


class SigpacImporterTest(TestCase):

    @override_settings(ERROR_HANDLER=['DBErrorHandler'])
    def test_createParcelDocument_raises_exception_when_no_params(self):
        self.assertRaises(ItacylException, sigpac.createParcelDocument, [])

    @override_settings(ERROR_HANDLER=['DBErrorHandler'])
    def test_createParcelDocument_raises_exception_when_bad_params(self):
        self.assertRaises(ItacylException,
                          sigpac.createParcelDocument,
                          [410991618, 8274.60336, 368.00616,
                           'no number', 1, 0, 0, 507, 435, 1, 0, 'TA'])
        self.assertRaises(ItacylException,
                          sigpac.createParcelDocument,
                          [410991618, 8274.60336, 368.00616,
                           'no number', 1, 0, 0, 507])
        self.assertRaises(ItacylException,
                          sigpac.createParcelDocument,
                          [410991618, 8274.60336, 368.00616,
                           5.1, 1, 0, 0, 507, 435, 1, 0, 'TA'])

    @mock.patch('osc.importer.sigpac.ITACYL_PROTOCOL', 'file:///')
    @mock.patch('osc.importer.sigpac.ITACYL_FTP',
                '{}/osc/tests/importer/fixtures'.format(os.getcwd()))
    def test_wont_fail_when_updateMunicipality_from_mucipality_zip_url(self):
        province = '05_Avila'
        municipality = '05271_Comunidad-Arenas-San-Pedro-Candeleda.zip'
        sigpac.updateMunicipality(province, municipality)
        self.assertTrue(True, "shouldn't throw exceptions")

    @mock.patch('osc.importer.sigpac.ITACYL_PROTOCOL', 'file:///')
    @mock.patch('osc.importer.sigpac.ITACYL_FTP',
                '{}/osc/tests/importer/fixtures'.format(os.getcwd()))
    def test_wont_fail_when_updateMunicipality_with_inner_folder(self):
        province = '37_Salamanca'
        municipality = '37_901.zip'
        sigpac.updateMunicipality(province, municipality)
        self.assertTrue(True, "shouldn't throw exceptions")

    @mock.patch('osc.importer.sigpac.ITACYL_PROTOCOL', 'file:///')
    @mock.patch('osc.importer.sigpac.ITACYL_FTP',
                '{}/osc/tests/importer/fixtures'.format(os.getcwd()))
    @mock.patch('osc.importer.sigpac.updateParcel')
    def test_updateMunicipality_calls_updateParcel(self,
                                                   m_updateParcel):
        province = '37_Salamanca'
        municipality = '37284_Sanchotello.zip'
        sigpac.updateMunicipality(province, municipality)
        self.assertTrue(m_updateParcel.call_count == 10, 'Updates 10 parcels')
        m_updateParcel.assert_called()
        m_updateParcel.assert_called_with(
            {'doc':
                {'properties':
                    {'nationalCadastralReference': '37284A00100004',
                     'sigpacData': {'ZONA': 0,
                                    'PROVINCIA': 37,
                                    'USO_SIGPAC': 'IM',
                                    'RECINTO': 2,
                                    'PERIMETRO': 50.39169,
                                    'DN_OID': 895882,
                                    'PARCELA': 4,
                                    'POLIGONO': 1,
                                    'COEF_REGAD': 0,
                                    'SUPERFICIE': 121.32291,
                                    'AGREGADO': 0,
                                    'MUNICIPIO': 284}}}})

    @skip("Current development")
    def test_import_sigpac_data(self):
        sigpac.import_sigpac_data()
        self.fail('Not implemented yet')

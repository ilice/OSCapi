# coding=utf-8

from django.test import override_settings
from django.test import TestCase
import mock
from unittest import skip

from osc.exceptions import ItacylException
import osc.importer.sigpac as sigpac


class SigpacImporterTest(TestCase):

    @override_settings(ERROR_HANDLER=['DBErrorHandler'])
    def test_updateParcel_raises_exception_when_no_params(self):
        self.assertRaises(ItacylException, sigpac.updateParcel, [])

    @override_settings(ERROR_HANDLER=['DBErrorHandler'])
    def test_updateParcel_raises_exception_when_bad_params(self):
        self.assertRaises(ItacylException,
                          sigpac.updateParcel,
                          [410991618, 8274.60336, 368.00616,
                           'no number', 1, 0, 0, 507, 435, 1, 0, 'TA'])
        self.assertRaises(ItacylException,
                          sigpac.updateParcel,
                          [410991618, 8274.60336, 368.00616,
                           'no number', 1, 0, 0, 507])
        self.assertRaises(ItacylException,
                          sigpac.updateParcel,
                          [410991618, 8274.60336, 368.00616,
                           5.1, 1, 0, 0, 507, 435, 1, 0, 'TA'])

    @mock.patch('osc.importer.sigpac.ITACYL_PROTOCOL', 'file:///')
    @mock.patch('osc.importer.sigpac.ITACYL_FTP',
                'D:/teanocrata/Development/OSCapi/osc/tests/importer/fixtures')
    def test_wont_fail_when_updateMunicipality_from_mucipality_zip_url(self):
        province = '05_Avila'
        municipality = '05271_Comunidad-Arenas-San-Pedro-Candeleda.zip'
        sigpac.updateMunicipality(province, municipality)
        self.assertTrue(True, "shouldn't throw exceptions")

    @mock.patch('osc.importer.sigpac.ITACYL_PROTOCOL', 'file:///')
    @mock.patch('osc.importer.sigpac.ITACYL_FTP',
                'D:/teanocrata/Development/OSCapi/osc/tests/importer/fixtures')
    def test_wont_fail_when_updateMunicipality_with_inner_folder(self):
        province = '37_Salamanca'
        municipality = '37_901.zip'
        sigpac.updateMunicipality(province, municipality)
        self.assertTrue(True, "shouldn't throw exceptions")

    @skip("Current development")
    def test_import_sigpac_data(self):
        # sigpac.import_sigpac_data()
        self.fail('Not implemented yet')

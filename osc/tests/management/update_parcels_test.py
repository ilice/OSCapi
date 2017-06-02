from django.core.management import call_command
from django.test import TestCase
# from django.core.management.base import CommandError
import mock


class UpdateParcelsTest(TestCase):

    @mock.patch('osc.management.commands.update_parcels.'
                'update_parcel_by_cadastral_code')
    def test_call_update_parcel_by_catastral_code(
            self,
            mock_update_parcel_by_cadastral_code):
        cadastral_code = '40167A00805001'
        call_command('update_parcels', '--parcel=%s' % cadastral_code)
        mock_update_parcel_by_cadastral_code.assert_called_with(cadastral_code)

    @mock.patch('osc.management.commands.update_parcels.'
                'update_cadastre_information')
    def test_update_parcels(
            self,
            mock_update_cadastre_information):
            call_command('update_parcels')
            mock_update_cadastre_information.assert_called()

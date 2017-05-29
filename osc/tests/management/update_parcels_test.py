from django.core.management import call_command
from django.test import TestCase
from django.core.management.base import CommandError
from unittest import skip
import mock


class UpdateParcelsTest(TestCase):
    def test_fails_when_there_is_no_parcel_args(self):
        with self.assertRaises(CommandError):
            call_command('update_parcels')

    @mock.patch('osc.services.parcels.update_parcel_by_cadastral_code')
    def test_call_update_parcel_by_catastral_code(
            self,
            mock_update_parcel_by_cadastral_code):
        cadastral_code = '40167A00805001'
        call_command('update_parcels', '--parcel=%s' % cadastral_code)
        mock_update_parcel_by_cadastral_code.assert_called_with(cadastral_code)

    @skip
    def test_update_parcel(self):
        raise NotImplementedError("Update parcel")

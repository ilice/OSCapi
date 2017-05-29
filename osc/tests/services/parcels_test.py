from django.test import TestCase
import mock

import osc.services.parcels as parcels


class UpdateParcelTest(TestCase):

    @mock.patch('osc.services.parcels.obtain_parcels_by_cadastral_code')
    def test_update_parcel_by_catastral_code(
            self,
            mock_obtain_parcels_by_cadastral_code):
        cadastral_code = '40167A00805001'
        parcels.update_parcel_by_cadastral_code(cadastral_code)
        mock_obtain_parcels_by_cadastral_code.assert_called_with(
            cadastral_code,
            retrieve_public_info=True,
            retrieve_climate_info=True,
            retrieve_soil_info=True)

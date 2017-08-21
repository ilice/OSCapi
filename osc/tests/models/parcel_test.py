from django.test import TestCase
import json
import logging
import mock
from nose.plugins.attrib import attr

from osc.models.parcel import getParcelByNationalCadastralReference
from osc.models.parcel import getParcels

logger = logging.getLogger(__name__)


class ParcelTest(TestCase):

    fixture_file = 'osc/tests/util/fixtures/get_parcel_by_bbox_response.json'

    with open(fixture_file) as data_file:
        get_parcel_by_bbox_response = json.load(data_file)

    @mock.patch('osc.models.parcel.es')
    def test_getParcelByNationalCadastralReference_runs_without_errors(self, mock_es):
        mock_es.search.return_value = self.get_parcel_by_bbox_response
        logger.debug(getParcelByNationalCadastralReference(nationalCadastralReference='37284A00600106'))

    @mock.patch('osc.models.parcel.es')
    def test_getParcelByNationalCadastralReference_calls_elastic_once(self, mock_es):
        mock_es.search.return_value = self.get_parcel_by_bbox_response
        getParcelByNationalCadastralReference(nationalCadastralReference='37284A00600106')
        mock_es.search.assert_called_once()

    @attr('elastic_connection')
    def test_getParcels(self):
        logger.debug(getParcels())

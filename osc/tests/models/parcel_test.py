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

    @mock.patch('osc.models.parcel.es')
    def test_getParcel_calls_elastic_once(self, mock_es):
        mock_es.search.return_value = self.get_parcel_by_bbox_response
        getParcels(bbox='40.435861,-5.763941,40.441145,-5.746592')
        mock_es.search.assert_called_with(
            body={
                'query':
                {
                    'bool':
                    {
                        'filter':
                        {
                            'geo_bounding_box':
                            {
                                'properties.reference_point':
                                {'top': '40.441145', 'bottom': '40.435861', 'left': '-5.763941', 'right': '-5.746592'}
                            }
                        },
                        'must': [
                            {'exists': {'field': 'properties.sigpacData'}},
                            {'exists': {'field': 'properties.elevation'}}
                        ]
                    }
                }
            },
            doc_type='parcel',
            index='parcels',
            size=5000)

    @mock.patch('osc.models.parcel.es')
    def test_getParcel_with_bbox_info_calls_elastic_once_with_bounds(self, mock_es):
        mock_es.search.return_value = self.get_parcel_by_bbox_response
        getParcels()
        mock_es.search.assert_called_once()

    @attr('elastic_connection')
    def test_getParcels(self):
        logger.debug(getParcels())

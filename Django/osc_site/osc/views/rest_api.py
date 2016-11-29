import osc.services.google as google_service
import osc.services.parcels as parcel_service
import osc.services.crop as crop_service

from osc.exceptions import OSCException

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class GoogleElevationList(APIView):
    """
    Obtain elevations from google from google
    """
    def get(self, request, format=None):
        param = request.GET.get('locations', '')

        if param == '':
            return Response({'error': 'Altitude Request should bring locations'},
                            status=status.HTTP_400_BAD_REQUEST)

        if param != '':
            locations_param = map(lambda x: float(x), param.split(','))

            response = google_service.obtain_elevation_from_google([locations_param])

            return Response(response)


class ParcelList(APIView):
    """
    Obtain parcels with associated information
    """

    def get(self, request, format=None):
        try:
            bbox_param = request.GET.get('bbox', None)
            cadastral_code_param = request.GET.get('cadastral_code', None)

            parcels = []

            if cadastral_code_param is not None:
                retrieve_public_info_param = request.GET.get('retrieve_public_info', None)
                retrieve_climate_info_param = request.GET.get('retrieve_climate_info', None)
                retrieve_soil_info_param = request.GET.get('retrieve_soil_info', None)

                parcels = parcel_service.obtain_parcels_by_cadastral_code(cadastral_code_param,
                                                                          retrieve_public_info_param == 'True',
                                                                          retrieve_climate_info_param == 'True',
                                                                          retrieve_soil_info_param == 'True')
            elif bbox_param is not None:
                lat_min, lon_min, lat_max, lon_max = map(lambda x: float(x), bbox_param.split(','))

                parcels = parcel_service.obtain_parcels_by_bbox(lat_min, lon_min, lat_max, lon_max)

            # Convert into geojson
            for parcel in parcels:
                parcel['type'] = 'Feature'

            parcels_geojson = {'type': 'FeatureCollection',
                               'features': parcels}

            return Response(parcels_geojson)
        except OSCException as e:
            return Response({'error': str(type(e)) + ': ' + e.message})


class CropList(APIView):
    def post(self, request, format=None):
        query = request.data

        try:
            crops = crop_service.retrieve_crops_from_elastic(query)
            return Response({'status': 'SUCCESS',
                             'result': crops})
        except Exception as e:
            return Response({'status': 'FAILURE',
                             'message': e.message},
                            status=status.HTTP_400_BAD_REQUEST)


class CropDetail(APIView):
    def put(self, request, crop_id, format=None):
        query = request.data

        try:
            crop_service.update_crops_in_elastic(crop_id, query)
            return Response({'status': 'SUCCESS'})
        except Exception as e:
            return Response({'status': 'FAILURE',
                             'message': e.message},
                            status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, crop_id, format=None):
        query = request.data

        try:
            crop_service.index_crops_in_elastic(crop_id, query)
            return Response({'status': 'SUCCESS'})
        except Exception as e:
            return Response({'status': 'FAILURE',
                             'message': e.message},
                            status=status.HTTP_400_BAD_REQUEST)


from osc.exceptions import OSCException
from osc.models import UserParcel
from osc.serializers import UserParcelSerializer
import osc.services.crop as crop_service
import osc.services.google as google_service
import osc.services.parcels as parcel_service
import osc.services.users as users_service

from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework import viewsets


class GoogleElevationList(APIView):
    """Obtain elevations from google from google"""

    def get(self, request, format=None):
        param = request.query_params.get('locations', '')

        if param == '':
            return Response(
                {'error': 'Altitude Request should bring locations'},
                status=status.HTTP_400_BAD_REQUEST)

        if param != '':
            locations_param = map(lambda x: float(x), param.split(','))

            response = google_service.obtain_elevation_from_google(
                [locations_param])

            return Response(response)


class ParcelList(APIView):
    """Obtain parcels with associated information"""

    def get(self, request):
        try:
            bbox_param = request.query_params.get('bbox', None)
            cadastral_code_param = request.query_params.get('cadastral_code',
                                                            None)
            precision_param = request.query_params.get('precision', None)

            parcels = []

            if cadastral_code_param is not None:
                retrieve_public_info_param = \
                    request.query_params.get('retrieve_public_info', None)
                retrieve_climate_info_param = \
                    request.query_params.get('retrieve_climate_info', None)
                retrieve_soil_info_param = \
                    request.query_params.get('retrieve_soil_info', None)

                parcels = parcel_service.obtain_parcels_by_cadastral_code(
                    cadastral_code_param,
                    retrieve_public_info_param == 'True',
                    retrieve_climate_info_param == 'True',
                    retrieve_soil_info_param == 'True')
            elif bbox_param is not None:
                lat_min, lon_min, lat_max, lon_max = map(lambda x: float(x),
                                                         bbox_param.split(','))

                if precision_param is not None:
                    precision = float(precision_param)
                else:
                    precision = 0

                parcels = parcel_service.obtain_parcels_by_bbox(lat_min,
                                                                lon_min,
                                                                lat_max,
                                                                lon_max,
                                                                precision)

            return Response(parcels)
        except OSCException as e:
            message = '%s: %s - %s' % (type(e), e.message, e.cause)
            return Response({'error': message})


class CropList(APIView):
    parser_classes = (JSONParser,)

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
    parser_classes = (JSONParser,)

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


class UserParcelsList(APIView):
    parser_classes = (JSONParser,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        username = request.user
        retrieve_public_info_param = \
            request.query_params.get('retrieve_public_info', None)
        retrieve_climate_info_param = \
            request.query_params.get('retrieve_climate_info', None)
        retrieve_soil_info_param = \
            request.query_params.get('retrieve_soil_info', None)

        try:
            parcels = users_service.get_parcels(
                username,
                retrieve_public_info_param == 'True',
                retrieve_climate_info_param == 'True',
                retrieve_soil_info_param == 'True')

            return Response(parcels, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'msg': e.message},
                            status=status.HTTP_400_BAD_REQUEST)


class UserParcelsDetail(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, format=None):
        username = request.user
        cadastral_code = request.data['cadastral_code'] \
            if 'cadastral_code' in request.data else None

        if cadastral_code is not None:
            try:
                user_parcel = \
                    users_service.add_parcel(username, cadastral_code)
                serializer = \
                    UserParcelSerializer(user_parcel)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'msg': e.message},
                                status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_400_BAD_REQUEST)


class UserDetail(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        user = request.user
        return Response(
            data={'username': user.username,
                  'first_name': user.first_name,
                  'last_name': user.last_name,
                  'email': user.email,
                  'loginMethod': user.username[0:user.username.find('_')],
                  'picture_link': user.userprofile.picture_link,
                  'parcels': users_service.get_parcels(user.username,
                                                       False,
                                                       False,
                                                       False)},
            status=status.HTTP_200_OK)


class OwnedParcels(APIView):
    parser_classes = (JSONParser,)

    def get(self, request, format=None):

        return Response(
            data={'parcels': users_service.get_parcels(None,
                                                       True,
                                                       False,
                                                       False)},
            status=status.HTTP_200_OK)


class UserParcelSet(viewsets.ModelViewSet):
    """API endpoint that allows user parcel to be viewed or edited. """
    queryset = UserParcel.objects.all()
    serializer_class = UserParcelSerializer


class APIRootView(APIView):
    def get(self, request):
        data = {
            'altitude': reverse('altitud', request=request),
            'cadastral_parcel': reverse('get_cadastral_parcels',
                                        request=request),
            'crops': reverse('obtain_crops_elastic_query', request=request),
            # 'crop': reverse('update_crops_elastic', request=request),
            'userparcel': reverse('obtain_user_parcels', request=request),
            'userparcel_add': reverse('add_user_parcel', request=request),
            'user-url': reverse('get_user', args=[], request=request),
            'owned-parcels': reverse('get_owned_parcels', request=request),
            'api-root': reverse('api-root', request=request)
        }
        return Response(data)

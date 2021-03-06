from osc.exceptions import OSCException
from osc.models.parcel import getParcelByNationalCadastralReference
from osc.models.parcel import getParcels
from osc.models import UserParcel
from osc.serializers import UserParcelSerializer
import osc.services.crop as crop_service
import osc.services.google as google_service
import osc.services.parcels as parcel_service
import osc.services.users as users_service

from rest_framework import generics
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework import viewsets


class GoogleElevationList(generics.RetrieveAPIView):
    """Obtain elevations from google from google"""
    permission_classes = (IsAuthenticated,)

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
    permission_classes = (IsAuthenticated,)

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
    permission_classes = (IsAuthenticated,)

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
    """Returns active users. """
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
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):

        return Response(
            data={'parcels': users_service.get_parcels(None,
                                                       True,
                                                       False,
                                                       False)},
            status=status.HTTP_200_OK)


class UserParcelSet(viewsets.ModelViewSet):
    """API endpoint that allows user parcel to be viewed or edited. """
    permission_classes = (IsAuthenticated,)
    queryset = UserParcel.objects.all()
    serializer_class = UserParcelSerializer


class ParcelViewSet(viewsets.ViewSet):
    """A parcel is the core entity from [OSC][osc].

    Its format is [GeoJSON][geojson], a format for encoding geographic data
    structures, each parcel is a Feature with a [Polygon][polygon] geometry
    type.

    ### List parcels
        GET /parcels
    <table class="table table-condensed">
        <tr>
            <th>URL Parameter</th>
            <th>Default</th>
            <th>Description</th>
            <th>Example</th>
        </tr>
        <tr>
            <td>cadastralReference</td>
            <td>None</td>
            <td>[Official and obligatory identifier of real estate][cadastralReference], it consist of 14 characters: the first two identify the province, the next three the municipality, the following is the character corresponding to the sector, pointing aggregate or zone reparcelling (if any), the following three identify the polygon (the municipality is divided into polygons based homogeneity crop, existence of geographical features, etc.), the following five identify each parcel within the corresponding polygon.</td>
            <td>37284A00600106</td>
        </tr>
    </table>

    <table class="table table-condensed">
        <tr>
            <th>Query Parameter</th>
            <th>Default</th>
            <th>Description</th>
            <th>Example</th>
        </tr>
        <tr>
            <td>bbox</td>
            <td>None</td>
            <td>Filter parcels using a bounding box. Array values are west, south, east, north</td>
            <td>?bbox=-5.763941,40.435861,-5.746592,40.441145</td>
        </tr>
        <tr>
            <td>precision</td>
            <td>None</td>
            <td>Agreggregates parcels and group it into buckets that represent cells ins a grid, can have a choice of presision between 1 and 12.</td>
            <td>?bbox=-5.763941,40.435861,-5.746592,40.441145&precission=5</td>
        </tr>
    </table>
    ### Show parcel
        GET /parcels/{cadastralReference}

    [osc]: https://opensmartcountry.com/ "Open Smart Country"
    [geojson]: http://geojson.org/ "GeoJSON Home Page"
    [polygon]: https://tools.ietf.org/html/rfc7946#section-3.1.6 "The GeoJSON Polygon Specification (RFC 7946)"
    [cadastralReference]: http://www.catastro.meh.es/esp/referencia_catastral.asp
    """

    def list(self, request):
        bbox = request.query_params.get('bbox', None)
        precision = request.query_params.get('precision', None)
        return Response(getParcels(request=request, bbox=bbox, precision=precision))

    def retrieve(self, request, pk=""):
        try:
            parcel = getParcelByNationalCadastralReference(nationalCadastralReference=pk)
        except KeyError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(parcel)


class OpenSmartCountryApiView(APIView):
    """Welcome to the OSC API. This is the entry point for the API used by
    [Open Smart Country][osc], so almost everything the web ui is able to do
    can also be accomplished via the API.

    Follow the hyperlinks each resource offers to explore the API.

    Note that you can also explore the API from the command line, for instance
    using the `curl` command-line tool.

    For example: `curl -X GET https://opensmartcountry.com/api -H "Accept: application/json; indent=4"`
    [osc]: https://opensmartcountry.com/ "Open Smart Country"
    """
    def get(self, request):
        data = {
            # TODO(teanocrata): comented because if you follow the link, updates inforiego daily!!!
            # 'inforiego_daily': reverse('update_inforiego_daily', request=request),
            'altitude': reverse('altitud', request=request),
            'cadastral_parcel': reverse('get_cadastral_parcels',
                                        request=request),
            'crops': reverse('obtain_crops_elastic_query', request=request),
            # 'crop': reverse('update_crops_elastic', request=request),
            'userparcel': reverse('obtain_user_parcels', request=request),
            'userParcels': reverse('userParcel-list', request=request),
            'userparcel_add': reverse('add_user_parcel', request=request),
            'user-url': reverse('get_user', args=[], request=request),
            'owned-parcels': reverse('get_owned_parcels', request=request),
            'api-root': reverse('api-root', request=request),
            'parcels': reverse('parcels-list', request=request),
            'auth-signIn': reverse('auth_signIn', request=request),
            # TODO(teanocrata): arguments
            # 'auth-update-user': reverse('auth_update_user', request=request),
            # 'auth-login': reverse('auth_login', request=request),
            # 'api-auth': reverse('api_auth', request=request),

        }
        return Response(data)

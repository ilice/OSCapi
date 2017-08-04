from django.http import HttpResponse
import json
from osc.services.parcels import obtain_parcels_by_cadastral_code
from osc.util.parser import Parcel
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets


def parcel_detail(request, cadastralReference=""):
    parcels = obtain_parcels_by_cadastral_code(cadastralReference)
    return HttpResponse(json.dumps(parcels), content_type='application/json')


def parcel_list(request):
    return HttpResponse({'bla': 'ble'}, content_type='application/json')


class ParcelViewSet(viewsets.ViewSet):
    """Parcel information"""

    fixture_file = 'osc/tests/util/fixtures/get_parcel_by_bbox_response.json'
    with open(fixture_file) as data_file:
        get_parcel_by_bbox_response = json.load(data_file)

    def list(self, request):
        hits = self.get_parcel_by_bbox_response['hits']['hits']
        parcels = []
        for parcelDocument in hits:
            parcels.append(Parcel(nationalCadastralReference=parcelDocument['_source']['properties']['nationalCadastralReference']).toGeoJSON)
        # serializer = serializers.ParcelSerializer(
        #     instance=parcels, many=True)
        return Response(parcels)

    def retrieve(self, request, pk=""):
        try:
            parcel = Parcel(nationalCadastralReference=pk)
        except KeyError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(parcel.toGeoJSON)

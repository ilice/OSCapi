from django.http import JsonResponse
from osc.services.importer import get_cadastral_parcels_by_code, get_cadastral_parcels_by_bbox, get_public_cadastre_info
from osc.services.elastic import get_closest_station, get_aggregated_climate_measures


def obtain_catastral_parcels(request):
    bbox_param = request.GET.get('bbox', None)
    cadastral_code_param = request.GET.get('cadastral_code', None)
    retrieve_public_info_param = request.GET.get('retrieve_public_info', None)
    retrieve_climate_info_param = request.GET.get('retrieve_climate_info', None)

    parcels = []

    if cadastral_code_param is not None:
        parcels = get_cadastral_parcels_by_code(cadastral_code_param)

        # Add public info
        if retrieve_public_info_param == 'True':
            for parcel in parcels:
                public_info = get_public_cadastre_info(cadastral_code_param)
                parcel['properties']['cadastralData'] = public_info

        # Add climate info
        if retrieve_climate_info_param == 'True':
            for parcel in parcels:
                closest_station = \
                    get_closest_station(parcel['properties']['reference_point']['lat'],
                                        parcel['properties']['reference_point']['lon'])
                climate_agg = get_aggregated_climate_measures(closest_station['IDESTACION'],
                                                              closest_station['IDPROVINCIA'],
                                                              3)
                parcel['properties']['climate_aggregations'] = climate_agg

    elif bbox_param is not None:
        lon_min, lat_min, lon_max, lat_max = map(lambda x: float(x), bbox_param.split(','))

        parcels = get_cadastral_parcels_by_bbox(lat_min, lon_min, lat_max, lon_max)

    # Convert into geojson
    for parcel in parcels:
        parcel['type'] = 'Feature'

    parcels_geojson = {'type': 'FeatureCollection',
                       'features': parcels}

    return JsonResponse(parcels_geojson)


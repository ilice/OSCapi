from django.http import JsonResponse
from osc.services import get_cadastral_parcels_by_code, get_cadastral_parcels_by_bbox, get_public_cadastre_info
from osc.services.climate import get_closest_station, get_aggregated_climate_measures
from osc.services.google import obtain_elevation_from_google
from osc.exceptions import OSCException


def is_valid_parcel(parcel):
    is_valid = True

    try:
        public_info = get_public_cadastre_info(parcel['properties']['nationalCadastralReference'])
        if public_info is not None:
            is_valid = public_info['bico']['lspr']['spr']['dspr']['ccc'] not in ['VT', 'OT', 'FF']
    except KeyError:
        # As it does not have information about the type, we assume that it is OK
        is_valid = True

    return is_valid


def obtain_cadastral_parcels(request):
    try:
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
            lat_min, lon_min, lat_max, lon_max = map(lambda x: float(x), bbox_param.split(','))

            parcels = get_cadastral_parcels_by_bbox(lat_min, lon_min, lat_max, lon_max)

            # Filter the parcels that are roads, ways, etc.
            # (JLG ATTENTION: To be removed when we have everything in ELASTIC)
            parcels = filter(is_valid_parcel, parcels)

        # Convert into geojson
        for parcel in parcels:
            parcel['type'] = 'Feature'


        # Add elevation from google
        try:
            centers = [(parcel['properties']['reference_point']['lat'],
                        parcel['properties']['reference_point']['lon']) for parcel in parcels]

            elevations = obtain_elevation_from_google(centers)

            if elevations is not None:
                for item in zip(elevations, parcels):
                    item[1]['properties']['elevation'] = item[0]

        except KeyError:
            pass

        parcels_geojson = {'type': 'FeatureCollection',
                           'features': parcels}

        return JsonResponse(parcels_geojson)
    except OSCException as e:
        return JsonResponse({'error': str(type(e)) + ': ' + e.message})



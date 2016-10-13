from django.http import JsonResponse
from osc.services.importer import get_catastral_parcels


def obtain_catastral_parcels(request):
    bbox_param = request.GET.get('bbox', None)

    if bbox_param is None:
        return JsonResponse('')

    lat_min, lon_min, lat_max, lon_max = map(lambda x: float(x), bbox_param.split(','))

    parcels = get_catastral_parcels(lat_min, lon_min, lat_max, lon_max)

    return JsonResponse({'status': 'OK',
                         'response': parcels})



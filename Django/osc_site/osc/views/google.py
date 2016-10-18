from django.http import JsonResponse

from osc.services import google


def altitud(request):
    param = request.GET.get('locations', '')

    if param == '':
        return JsonResponse({'error': 'Altitude Request should bring locations'})

    if param != '':
        locations_param = map(lambda x: float(x), param.split(','))

        response = google.obtain_elevation_from_google([locations_param])

        return JsonResponse(response)

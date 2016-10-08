from django.shortcuts import render
from django.http import JsonResponse

from services import google


def index(request):
    return render(request, 'osc/home.html', {})


def altitud(request):
    param = request.GET.get('locations', '')

    if param == '':
        return JsonResponse('{}')

    if param != '':
        locations_param = map(lambda x: float(x), param.split(','))

        response = google.obtain_elevation_from_google([locations_param])

        return JsonResponse(response)

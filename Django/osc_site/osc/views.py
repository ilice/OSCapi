from django.shortcuts import render
from django.http import JsonResponse
from django.core import serializers

from util import google


def index(request):
    return render(request, 'osc/index.html', {})


def cultivos(request):
    return render(request, 'osc/cultivos.html', {})


def parcela(request):
    return render(request, 'osc/parcela.html', {})


def oscar(request):
    return render(request, 'osc/oscar.html', {})


def mapa_de_parcelas(request):
    return render(request, 'osc/mapaDeParcelas.html', {})


def altitud(request):
    param = request.GET.get('locations', '')

    if param == '':
        return JsonResponse('{}')

    if param != '':
        locations_param = map(lambda x: float(x), param.split(','))

        response = google.obtain_elevation_from_google([locations_param])

        return JsonResponse(response)

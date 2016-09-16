from django.shortcuts import render


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

from django.shortcuts import render


def index(request):
    return render(request, 'osc/index.html')


def propietario(request):
    return render(request, 'osc/propietario.html')


def mapa_de_parcelas(request):
    return render(request, 'osc/mapaDeParcelas.html')


def team(request):
    return render(request, 'osc/team.html')


def parcela(request):
    return render(request, 'osc/parcela.html')


def cultivo(request):
    return render(request, 'osc/cultivo.html')


def cultivos(request):
    return render(request, 'osc/cultivos.html')

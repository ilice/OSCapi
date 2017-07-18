from django.http import HttpResponse


def parcel(request, parcel_id=""):
    return HttpResponse(content_type='application/json')

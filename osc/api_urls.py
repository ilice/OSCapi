from django.conf.urls import url
from osc import api

urlpatterns = [
    url(r'^parcels/$', api.parcel, name='api_parcel'),
]

from django.conf.urls import url
from osc import api

urlpatterns = [
    url(r'^parcels/$', api.parcel_list, name='api_parcels'),
    url(r'^parcels/(\w+)/$', api.parcel_detail, name='api_parcel'),
]

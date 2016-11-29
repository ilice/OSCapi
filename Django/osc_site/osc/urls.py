from django.conf.urls import url

from osc.views import rest_api
from osc.views import jobs
from osc.views import crop
from osc.views import web
from osc.views import google
from osc.views import cadastre


urlpatterns = [
    # Relative to the web
    url(r'^propietario/$', web.propietario, name='propietario'),
    url(r'^mapaDeParcelas/$', web.mapa_de_parcelas, name='mapa_de_parcelas'),
    url(r'^parcela/$', web.parcela, name='parcela'),
    url(r'^team/$', web.team, name='team'),
    url(r'^cultivo/$', web.cultivo, name='cultivo'),
    url(r'^cultivos/$', web.cultivos, name='cultivos'),

    # Jobs (to be removed)
    url(r'^inforiego_daily/update/$', jobs.update_inforiego_daily, name='update_inforiego_daily'),

    # Another services (old)
    url(r'^altitud/$', google.altitud, name='altitud'),
    url(r'^inforiego_daily/update/$', jobs.update_inforiego_daily, name='update_inforiego_daily'),
    url(r'^cadastral/parcel/$', cadastre.obtain_cadastral_parcels, name='get_cadastral_parcels'),
    url(r'^crops/elastic/search/$', crop.obtain_crops_elastic_query, name='obtain_crops_elastic_query'),
    url(r'^crops/elastic/update/(?P<crop_id>[0-9]+)/$', crop.update_crops_elastic, name='update_crops_elastic'),
    url(r'^crops/elastic/index/(?P<crop_id>[0-9]+)/$', crop.index_crops_elastic, name='index_crops_elastic'),

    # Another services (new)
    # url(r'^altitud/$', rest_api.GoogleElevationList.as_view(), name='altitud'),
    # url(r'^cadastral/parcel/$', rest_api.ParcelList.as_view(), name='get_cadastral_parcels'),
    # url(r'^crops/elastic/search/$', rest_api.CropList.as_view(), name='obtain_crops_elastic_query'),
    # url(r'^crops/elastic/update/(?P<crop_id>[0-9]+)/$', crop.update_crops_elastic, name='update_crops_elastic'),
    # url(r'^crops/elastic/index/(?P<crop_id>[0-9]+)/$', crop.index_crops_elastic, name='index_crops_elastic')

    # Autentication

]

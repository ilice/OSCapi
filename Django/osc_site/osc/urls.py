from django.conf.urls import url

from osc.views import google
from osc.views import inforiego
from osc.views import cadastre
from osc.views import crop
from osc.views import web

urlpatterns = [
    # Relative to the web
    url(r'^$', web.index, name='index'),
    url(r'^propietario/$', web.propietario, name='propietario'),
    url(r'^mapaDeParcelas/$', web.mapa_de_parcelas, name='mapa_de_parcelas'),
    url(r'^parcela/$', web.parcela, name='parcela'),
    url(r'^team/$', web.team, name='team'),
    url(r'^cultivo/$', web.cultivo, name='cultivo'),
    url(r'^cultivos/$', web.cultivos, name='cultivos'),

    # Another services
    url(r'^altitud/$', google.altitud, name='altitud'),
    url(r'^inforiego_daily/update/$', inforiego.update_inforiego_daily, name='update_inforiego_daily'),
    url(r'^cadastral/parcel/$', cadastre.obtain_cadastral_parcels, name='get_cadastral_parcels'),
    url(r'^crops/elastic/search/$', crop.obtain_crops_elastic_query, name='obtain_crops_elastic_query'),
    url(r'^crops/elastic/update/(?P<crop_id>[0-9]+)/$', crop.update_crops_elastic, name='update_crops_elastic')
]

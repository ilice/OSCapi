from django.conf.urls import url

from osc.views import google
from osc.views import inforiego
from osc.views import cadastre
from osc.views import crop
from osc.views import web

urlpatterns = [
    url(r'^$', web.index, name='index'),
    url(r'^propietario/$', web.propietario, name='propietario'),
    url(r'^mapaDeParcelas/$', web.mapa_de_parcelas, name='mapa_de_parcelas'),
    url(r'^parcela/$', web.parcela, name='parcela'),
    url(r'^team/$', web.team, name='team'),
    url(r'^cultivo/$', web.cultivo, name='cultivo'),
    url(r'^cultivos/$', web.cultivos, name='cultivos'),

    url(r'^altitud/$', google.altitud, name='altitud'),
    url(r'^inforiego_daily/update$', inforiego.update_inforiego_daily, name='update_inforiego_daily'),
    url(r'^cadastral/parcel$', cadastre.obtain_cadastral_parcels, name='get_cadastral_parcels'),
    url(r'^crops/elastic', crop.obtain_crops_elastic_query, name='obtain_crops_elastic_query'),
    # url(r'^inforiego_daily/cancel/($P<process_id>[0-9]*)/$', inforiego.cancel_inforiego_daily, name='cancel_inforiego_daily'),
    # url(r'^update/inforiego_hourly/$', views.update_inforiego_hourly, name='update_inforiego_hourly'),
]
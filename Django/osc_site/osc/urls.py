from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^cultivos/$', views.cultivos, name='cultivos'),
    url(r'^parcela/$', views.parcela, name='parcela'),
    url(r'^oscar/$', views.oscar, name='oscar'),
    url(r'^mapa_de_parcelas/$', views.mapa_de_parcelas, name='mapa_de_parcelas'),
]
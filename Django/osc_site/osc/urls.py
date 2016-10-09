from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^altitud/$', views.altitud, name='altitud'),
    # url(r'^update/inforiego_daily/$', views.update_inforiego_daily, name='update_inforiego_daily'),
    # url(r'^update/inforiego_hourly/$', views.update_inforiego_hourly, name='update_inforiego_hourly'),
]
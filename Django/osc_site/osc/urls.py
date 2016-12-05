from django.conf.urls import url

from osc.views import rest_api
from osc.views import jobs
from osc.views import web
from osc.views import auth
import rest_framework.authtoken.views as rf_views


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

    # Another services (new)
    url(r'^altitud/$', rest_api.GoogleElevationList.as_view(), name='altitud'),
    url(r'^cadastral/parcel/$', rest_api.ParcelList.as_view(), name='get_cadastral_parcels'),
    url(r'^crops/elastic/search/$', rest_api.CropList.as_view(), name='obtain_crops_elastic_query'),
    url(r'^crops/elastic/(?P<crop_id>[0-9]+)/$', rest_api.CropDetail.as_view(), name='update_crops_elastic'),
    url(r'^userparcel/query/$', rest_api.UserParcelsList.as_view(), name='obtain_user_parcels'),
    url(r'^userparcel/add/$', rest_api.UserParcelsDetail.as_view(), name='add_user_parcel'),
    url(r'^user/$', rest_api.UserDetail.as_view(), name='get_user_'),

    # Autentication
    url(r'^auth-create-user', auth.CreateUser.as_view()),
    url(r'^auth-update-user', auth.UpdateUser.as_view()),
    url(r'^auth-google-login', auth.GoogleLogin.as_view()),
    url(r'^auth-facebook-login', auth.FacebookLogin.as_view()),
    url(r'^auth-login', rf_views.obtain_auth_token),
]

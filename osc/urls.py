from django.conf.urls import include
from django.conf.urls import url

from osc import api
from osc.views import auth
from osc.views import jobs
from osc.views import rest_api

import rest_framework.authtoken.views as rf_views
from rest_framework import routers


router = routers.DefaultRouter()
router.register(r'userParcel', rest_api.UserParcelSet)

urlpatterns = [

    # Jobs (to be removed)
    url(r'^inforiego_daily/update/$', jobs.update_inforiego_daily,
        name='update_inforiego_daily'),

    # Another services (new)
    url(r'^altitud/$', rest_api.GoogleElevationList.as_view(), name='altitud'),
    url(r'^cadastral/parcel/$', rest_api.ParcelList.as_view(),
        name='get_cadastral_parcels'),
    url(r'^crops/elastic/search/$', rest_api.CropList.as_view(),
        name='obtain_crops_elastic_query'),
    # url(r'^crops/elastic/(?P<crop_id>[0-9]+)/$',
    #     rest_api.CropDetail.as_view(), name='update_crops_elastic'),
    url(r'^userparcel/query/$', rest_api.UserParcelsList.as_view(),
        name='obtain_user_parcels'),
    url(r'^userparcel/add/$', rest_api.UserParcelsDetail.as_view(),
        name='add_user_parcel'),
    url(r'^user/$', rest_api.UserDetail.as_view(), name='get_user'),
    url(r'^owned-parcels/$', rest_api.OwnedParcels.as_view(),
        name='get_owned_parcels'),

    url(r'^parcels/$', api.parcel_list, name='api_parcels'),
    url(r'^parcels/(\w+)/$', api.parcel_detail, name='api_parcel'),


    # Autentication
    url(r'^auth-signIn', auth.SignIn.as_view(), name='auth_signIn'),
    url(r'^auth-update-user', auth.UpdateUser.as_view()),
    url(r'^auth-login', rf_views.obtain_auth_token),

    # Rest framework
    url(r'^$', rest_api.OpenSmartCountryApiView.as_view()),
    url(r'^', include(router.urls)),
    url(r'^api-auth/',
        include('rest_framework.urls', namespace='rest_framework')),

]

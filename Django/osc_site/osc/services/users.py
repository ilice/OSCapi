from django.contrib.auth.models import User
from osc.models import UserProfile, UserParcel

import osc.services.parcels as parcel_service


def get_user(username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = None

    return user


def get_parcels(username, retrieve_public_info=False, retrieve_climate_info=False, retrieve_soil_info=False):
    user = get_user(username)
    user_parcels = UserParcel.objects.filter(user=user)

    parcels = []
    for user_parcel in user_parcels:
        parcels += parcel_service.obtain_parcels_by_cadastral_code(user_parcel.cadastral_code,
                                                                   retrieve_public_info=retrieve_public_info,
                                                                   retrieve_climate_info=retrieve_climate_info,
                                                                   retrieve_soil_info=retrieve_soil_info)
    return parcels


def add_parcel(username, cadastral_code):
    user = get_user(username)

    if user is not None:
        try:
            user_parcel = UserParcel.objects.get(user=user, cadastral_code=cadastral_code)

        except UserParcel.DoesNotExist:
            user_parcel = UserParcel.objects.create(user=user, cadastral_code=cadastral_code)

        return user_parcel

    return None

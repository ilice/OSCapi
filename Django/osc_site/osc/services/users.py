from django.contrib.auth.models import User
from osc.models import UserProfile, UserParcel

import osc.services.parcels as parcel_service


def get_user(username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = None

    return user


def get_user_profile(username):
    user_profile = None

    user = get_user(username)
    if user is not None:
        user_profile = UserProfile.objects.get(user=user)

    return user_profile


def create_user(username,
                password,
                given_name,
                family_name,
                email=None,
                gender=None,
                link=None,
                locale=None,
                picture_link=None):
    if get_user(username) is not None:
        return None

    user = User.objects.create_user(username=username,
                                    password=password,
                                    email=email,
                                    first_name=given_name,
                                    last_name=family_name)
    user.save()

    update_user_profile(username,
                        email=email,
                        family_name=family_name,
                        given_name=given_name,
                        gender=gender,
                        link=link,
                        picture_link=picture_link,
                        locale=locale)

    return user


def update_user_profile(username,
                        password=None,
                        email=None,
                        family_name=None,
                        gender=None,
                        given_name=None,
                        google_id=None,
                        facebook_id=None,
                        link=None,
                        locale=None,
                        picture_link=None):
    user = get_user(username)

    if user is not None:
        if password is not None:
            user.set_password(password)
            
        user.email = email if email is not None else user.email
        user.first_name = given_name if given_name is not None else user.first_name
        user.last_name = family_name if family_name is not None else user.family_name

        user.save()

        profile = get_user_profile(username)

        profile.gender = gender if gender is not None else profile.gender
        profile.google_id = google_id if google_id is not None else profile.google_id
        profile.facebook_id = facebook_id if facebook_id is not None else profile.facebook_id
        profile.link = link if link is not None else profile.link
        profile.locale = locale if locale is not None else profile.locale
        profile.picture_link = picture_link if picture_link is not None else profile.picture_link

        profile.save()

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

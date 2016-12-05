# Google
import osc.services.users as users_service

from django.conf import settings

from requests_oauthlib import OAuth2Session
from rest_framework.authtoken.models import Token

from oauth2client import client, crypt


def get_token(username):
    user = users_service.get_user(username)
    token = None
    if user is not None:
        token, created = Token.objects.get_or_create(user=user)

    return token


def get_token_from_google_auth(google_auth_url):
    token = None

    google_client_id = settings.GOOGLE['auth_client_id']
    google_client_secret = settings.GOOGLE['auth_client_secret']
    google_token_url = "https://www.googleapis.com/oauth2/v4/token"
    google_scope = ["https://www.googleapis.com/auth/userinfo.email",
                    "https://www.googleapis.com/auth/userinfo.profile"]
    google_info_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    google_redirect_uri = "http://localhost:8000/auth-google-login"

    google = OAuth2Session(client_id=google_client_id, scope=google_scope, redirect_uri=google_redirect_uri)
    google.fetch_token(google_token_url, client_secret=google_client_secret, authorization_response=google_auth_url)

    response = google.get(google_info_url)

    if response.ok:
        json_response = response.json()
        google_id = json_response['id']
        email = json_response['email'] if 'email' in json_response else None
        family_name = json_response['family_name'] if 'family_name' in json_response else None
        gender = json_response['gender'] if 'gender' in json_response else None
        given_name = json_response['given_name'] if 'given_name' in json_response else None
        link = json_response['link'] if 'link' in json_response else None
        locale = json_response['locale'] if 'locale' in json_response else None
        picture_url = json_response['picture'] if 'picture' in json_response else None

        username = 'google_' + google_id

        user = users_service.get_user(username)
        if user is None:
            users_service.create_user(username,
                                      password=google_info_url,
                                      given_name=given_name,
                                      family_name=family_name)

        users_service.update_user_profile(username,
                                          email=email,
                                          family_name=family_name,
                                          gender=gender,
                                          given_name=given_name,
                                          google_id=google_id,
                                          link=link,
                                          locale=locale,
                                          picture_link=picture_url)

        token = get_token(username)

    return token

def get_token_from_google_token(googleToken):
    token = None
    
    google_client_id = settings.GOOGLE['auth_client_id']
    google_info_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    
    try:
        idinfo = client.verify_id_token(googleToken, google_client_id)
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise crypt.AppIdentityError("Wrong issuer.")

    
        google_id = idinfo['sub'] if 'sub' in idinfo else None
        email = idinfo['email'] if 'email' in idinfo else None
        family_name = idinfo['family_name'] if 'family_name' in idinfo else None
        gender = idinfo['gender'] if 'gender' in idinfo else None
        given_name = idinfo['given_name'] if 'given_name' in idinfo else None
        link = idinfo['link'] if 'link' in idinfo else None
        locale = idinfo['locale'] if 'locale' in idinfo else None
        picture_url = idinfo['picture'] if 'picture' in idinfo else None
        
        username = 'google_' + google_id
        
        user = users_service.get_user(username)
        if user is None:
            users_service.create_user(username,
                                      password=google_info_url,
                                      given_name=given_name,
                                      family_name=family_name)

        users_service.update_user_profile(username,
                                          email=email,
                                          family_name=family_name,
                                          gender=gender,
                                          given_name=given_name,
                                          google_id=google_id,
                                          link=link,
                                          locale=locale,
                                          picture_link=picture_url)

        token = get_token(username)
        
    except crypt.AppIdentityError:
        # Invalid token
        return 'error'
        
    return token
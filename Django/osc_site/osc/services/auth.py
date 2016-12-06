import osc.services.users as users_service

from django.conf import settings

from rest_framework.authtoken.models import Token

from oauth2client import client, crypt

import facebook


def get_token(username):
    user = users_service.get_user(username)
    token = None
    if user is not None:
        token, created = Token.objects.get_or_create(user=user)

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
        
    return username, token

def get_token_from_facebook_token(facebookToken):
    
    graph = facebook.GraphAPI(access_token=facebookToken, version='2.2')
    profile = graph.get_object("me", fields='email,first_name,gender,last_name,locale,name,timezone,link,birthday,age_range,id')
        
    
    
    facebook_id = profile['id'] if 'id' in profile else None
    email = profile['email'] if 'email' in profile else None
    family_name = profile['last_name'] if 'last_name' in profile else None
    gender = profile['gender'] if 'gender' in profile else None
    given_name = profile['first_name'] if 'first_name' in profile else None
    link = profile['link'] if 'link' in profile else None
    locale = profile['locale'] if 'locale' in profile else None
    picture_url = 'http://graph.facebook.com/' + facebook_id + '/picture'
    
    facebook_info_url = "https://graph.facebook.com/oauth/access_token"
        
    username = 'facebook_' + facebook_id
        
    user = users_service.get_user(username)
    if user is None:
        users_service.create_user(username,
                                  password=facebook_info_url,
                                  given_name=given_name,
                                  family_name=family_name)

    users_service.update_user_profile(username,
                                      email=email,
                                      family_name=family_name,
                                      gender=gender,
                                      given_name=given_name,
                                      facebook_id=facebook_id,
                                      link=link,
                                      locale=locale,
                                      picture_link=picture_url)
    token = get_token(username)
        
    return username, token


def get_token_from_email_and_password(email, password):
        
    family_name = email[:email.find('@')]
    given_name = email[:email.find('@')]
        
    username = email
        
    user = users_service.get_user(username)
    if user is None:
        users_service.create_user(username,
                                  password=password,
                                  given_name=given_name,
                                  family_name=family_name)
        
    users_service.update_user_profile(username,
                                      email=email,
                                      given_name=given_name,
                                      family_name=family_name)

    token = get_token(username)
        
    return username, token
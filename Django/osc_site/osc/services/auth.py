# Google

from django.conf import settings

google_client_id = settings.GOOGLE['auth_client_id']
google_client_secret = settings.GOOGLE['auth_client_id']
google_authorization_base_url = "https://accounts.google.com/o/oauth2/v2/auth"
google_token_url = "https://www.googleapis.com/oauth2/v4/token"
google_scope = [
     "https://www.googleapis.com/auth/userinfo.email",
     "https://www.googleapis.com/auth/userinfo.profile"
]


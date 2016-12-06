from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated

import osc.services.auth as auth_service
import osc.services.users as users_service

class SignIn(APIView):
    """
    Create a user given its authorization grant
    """
    renderer_classes = (JSONRenderer,)
    parser_classes = (JSONParser,)
    
    def post(self, request, format=None):
        
        authorizationGrant = request.data['authorizationGrant'] if 'authorizationGrant' in request.data else None
        googleAccessToken = authorizationGrant['googleAccessToken'] if 'googleAccessToken' in authorizationGrant else None
        facebookAccessToken = authorizationGrant['facebookAccessToken'] if 'facebookAccessToken' in authorizationGrant else None
        email = authorizationGrant['email'] if 'email' in authorizationGrant else None
        password = authorizationGrant['password'] if 'password' in authorizationGrant else None
        
        plot = authorizationGrant['plot'] if 'plot' in authorizationGrant else None
        plotRelation = authorizationGrant['plotRelation'] if 'plotRelation' in authorizationGrant else None
        
        if googleAccessToken is not None:
            username, token = auth_service.get_token_from_google_token(googleAccessToken)
        elif facebookAccessToken is not None:
            username, token = auth_service.get_token_from_facebook_token(facebookAccessToken)
        elif email is not None and password is not None:
            username, token = auth_service.get_token_from_email_and_password(email, password)
        else:
            return Response(data={'error': 'not enough data in request'}, status=status.HTTP_400_BAD_REQUEST)
        
        if plotRelation == 'myPlot':
            users_service.add_parcel(username, plot)

        return Response({'token': token.key}, status=status.HTTP_200_OK) 

class UpdateUser(APIView):
    """
    Create a user given its user and password
    """
    renderer_classes = (JSONRenderer,)
    parser_classes = (JSONParser,)
    permission_classes = (IsAuthenticated, )

    def put(self, request, format=None):
        username = request.user
        password = request.data['password'] if 'password' in request.data else None
        email = request.data['email'] if 'email' in request.data else None
        given_name = request.data['given_name'] if 'given_name' in request.data else None
        family_name = request.data['family_name'] if 'family_name' in request.data else None
        gender = request.data['gender'] if 'gender' in request.data else None
        link = request.data['link'] if 'link' in request.data else None
        locale = request.data['locale'] if 'locale' in request.data else None
        picture_link = request.data['picture'] if 'picture' in request.data else None

        if username is not None:
            user = users_service.update_user_profile(username,
                                                     password=password,
                                                     email=email,
                                                     family_name=family_name,
                                                     gender=gender,
                                                     given_name=given_name,
                                                     link=link,
                                                     locale=locale,
                                                     picture_link=picture_link)
            if user is None:
                return Response(data={'error': 'unexisting user'}, status=status.HTTP_412_PRECONDITION_FAILED)

        return Response({'msg': 'updated user ' + str(request.user)}, status=status.HTTP_200_OK)

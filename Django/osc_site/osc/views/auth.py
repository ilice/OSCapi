from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated

import osc.services.auth as auth_service
import osc.services.users as users_service
from osc.views.rest_api import UserParcelsDetail


class CreateUser(APIView):
    """
    Create a user given its user and password
    """
    renderer_classes = (JSONRenderer,)
    parser_classes = (JSONParser,)

    def post(self, request, format=None):
        username = request.data['username'] if 'username' in request.data else None
        password = request.data['password'] if 'password' in request.data else None
        email = request.data['email'] if 'email' in request.data else None
        given_name = request.data['given_name'] if 'given_name' in request.data else None
        family_name = request.data['family_name'] if 'family_name' in request.data else None
        gender = request.data['gender'] if 'gender' in request.data else None
        link = request.data['link'] if 'link' in request.data else None
        locale = request.data['locale'] if 'locale' in request.data else None
        picture_link = request.data['picture'] if 'picture' in request.data else None
        plot = request.data['plot'] if 'plot' in request.data else None
        plotRelation = request.data['plotRelation'] if 'plotRelation' in request.data else None

        if username is not None and password is not None:
            user = users_service.create_user(username, password,
                                             given_name,
                                             family_name,
                                             email=email,
                                             gender=gender,
                                             link=link,
                                             locale=locale,
                                             picture_link=picture_link)
            if user is None:
                return Response(data={'error': 'existing user'}, status=status.HTTP_412_PRECONDITION_FAILED)
        else:
            return Response(data={'error': 'no user in request'}, status=status.HTTP_400_BAD_REQUEST)

        user.save()
        
        token = auth_service.get_token(username)
        
        if plotRelation == 'myPlot':
            users_service.add_parcel(username, plot)
            
        return Response(data={'token': token.key}, status=status.HTTP_201_CREATED)


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


class GoogleLogin(APIView):
    """
    Create a user given its user and password
    """
    renderer_classes = (JSONRenderer,)
    parser_classes = (JSONParser,)

    def get(self, request, format=None):
        token = auth_service.get_token_from_google_auth('https://localhost:8000' + request.get_full_path())

        return Response({'token': token.key}, status=status.HTTP_200_OK)
    
    def post(self, request, format=None):
        googleToken = request.data['idtoken'] if 'idtoken' in request.data else None
        token = auth_service.get_token_from_google_token(googleToken)

        return Response({'token': token.key}, status=status.HTTP_200_OK)



class FacebookLogin(APIView):
    """
    Create a user given its user and password
    """
    renderer_classes = (JSONRenderer,)
    parser_classes = (JSONParser,)

    def put(self, request, format=None):
        pass

    def post(self, request, format=None):
        facebookToken = request.data['idtoken'] if 'idtoken' in request.data else None
        token = auth_service.get_token_from_facebook_token(facebookToken)

        return Response({'token': token.key}, status=status.HTTP_200_OK)

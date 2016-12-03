from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User


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
        first_name = request.data['firstname'] if 'firstname' in request.data else None
        last_name = request.data['lastname'] if 'lastname' in request.data else None

        if username is not None and password is not None:
            # Look for the user
            try:
                User.objects.get(username=username)
                return Response(data={'error': 'existing user'}, status=status.HTTP_412_PRECONDITION_FAILED)
            except User.DoesNotExist:
                user = User.objects.create_user(username=username,
                                                password=password,
                                                email=email,
                                                first_name=first_name,
                                                last_name=last_name)
        else:
            return Response(data={'error': 'no user in request'}, status=status.HTTP_400_BAD_REQUEST)

        token = Token.objects.get_or_create(user=user)

        return Response({'token': token})


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
        first_name = request.data['firstname'] if 'firstname' in request.data else None
        last_name = request.data['lastname'] if 'lastname' in request.data else None

        if username is not None:
            # Look for the user
            try:
                user = User.objects.get(username=username)
                if password is not None:
                    user.set_password(raw_password=password)

                user.email = email if user.email is None else user.email
                user.first_name = first_name if user.first_name is None else user.first_name
                user.last_name = last_name if user.last_name is None else user.last_name
                user.save()
            except User.DoesNotExist:
                return Response(data={'error': 'unexisting user'}, status=status.HTTP_412_PRECONDITION_FAILED)

        return Response({'msg': 'password changed for user ' + str(request.user)}, status=status.HTTP_200_OK)


class GoogleLogin(APIView):
    """
    Create a user given its user and password
    """
    renderer_classes = (JSONRenderer,)
    parser_classes = (JSONParser,)

    def put(self, request, format=None):
        pass


class FacebookLogin(APIView):
    """
    Create a user given its user and password
    """
    renderer_classes = (JSONRenderer,)
    parser_classes = (JSONParser,)

    def put(self, request, format=None):
        pass



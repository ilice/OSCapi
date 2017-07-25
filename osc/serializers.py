from osc.models import UserParcel
from osc.models import UserProfile
from rest_framework import serializers


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = UserProfile
        fields = ('user',)


class UserParcelSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = UserParcel
        fields = ('user', 'cadastral_code')

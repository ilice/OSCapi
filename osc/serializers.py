from rest_framework import serializers

from osc.models import UserParcel
from osc.models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = UserProfile
        fields = ('user',)


class UserParcelSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = UserParcel
        fields = ('user', 'cadastral_code')

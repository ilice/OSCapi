from rest_framework import serializers
from osc.models import UserProfile, UserParcel


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('user',)


class UserParcelSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserParcel
        fields = ('user', 'cadastral_code')
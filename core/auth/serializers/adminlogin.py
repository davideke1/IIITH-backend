from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.settings import api_settings
from django.contrib.auth.models import update_last_login
from django.contrib.auth import authenticate
from core.wqmsapi.serializers import UserSerializer  # Update to your actual UserSerializer path

class AdminLoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = authenticate(**{
            self.username_field: attrs[self.username_field],
            'password': attrs['password'],
        })

        if user:
            if not user.is_active:
                raise serializers.ValidationError("User account is not active.")
            if not user.is_staff:
                raise serializers.ValidationError("User does not have admin privileges.")
            refresh = self.get_token(user)
            data['user'] = UserSerializer(user).data
            data['refresh'] = str(refresh)
            data['access'] = str(refresh.access_token)
            if api_settings.UPDATE_LAST_LOGIN:
                update_last_login(None, user)
        else:
            raise serializers.ValidationError("Unable to log in with provided credentials.")

        return data

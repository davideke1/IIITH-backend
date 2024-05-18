from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.settings import api_settings
from django.contrib.auth.models import update_last_login
from django.contrib.auth import authenticate

from core.wqmsapi.serializers import UserSerializer

class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = authenticate(**{
            self.username_field: attrs[self.username_field],
            'password': attrs['password'],
        })

        if user:
            if not user.is_active:
                raise serializers.ValidationError({"detail": "User account is not active. Please contact support to reactivate your account."})

            refresh = self.get_token(user)
            data['user'] = UserSerializer(user).data
            data['refresh'] = str(refresh)
            data['access'] = str(refresh.access_token)
            if api_settings.UPDATE_LAST_LOGIN:
                update_last_login(None, user)
        else:
            raise serializers.ValidationError({"detail": "Unable to log in with provided credentials."})

        return data

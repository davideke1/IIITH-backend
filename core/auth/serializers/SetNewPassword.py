from rest_framework import serializers
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator
from django.utils.translation import gettext_lazy as _
from core.wqmsapi.models import CustomUser  # Adjust the import based on your project structure


class SetNewPasswordSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        try:
            uid = force_str(urlsafe_base64_decode(attrs['uidb64']))
            self.user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            raise serializers.ValidationError(_('Invalid user ID'))

        if not default_token_generator.check_token(self.user, attrs['token']):
            raise serializers.ValidationError(_('Invalid or expired token'))

        return attrs

    def save(self, **kwargs):
        password = self.validated_data['password']
        self.user.set_password(password)
        self.user.save()
        return self.user

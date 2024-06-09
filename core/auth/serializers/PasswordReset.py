# serializers.py
from rest_framework import serializers
from django.contrib.auth.tokens import default_token_generator
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.conf import settings
from core.wqmsapi.models import CustomUser

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            self.user = CustomUser.objects.get(email=value)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError(_('No user is associated with this email address.'))
        return value

    def save(self):
        token = default_token_generator.make_token(self.user)
        uid = self.user.pk

        # Construct password reset URL
        reset_url = f"{settings.FRONTEND_URL}/password-reset-confirm/{uid}/{token}/"

        # Send password reset email
        send_mail(
            subject="Password Reset Request",
            message=f"Click the following link to reset your password: {reset_url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.user.email],
        )


# from rest_framework import serializers

# class PasswordResetSerializer(serializers.Serializer):
#     email = serializers.EmailField()

# class SetNewPasswordSerializer(serializers.Serializer):
#     password = serializers.CharField(min_length=6, max_length=128)
#     token = serializers.CharField(write_only=True)
#     uidb64 = serializers.CharField(write_only=True)

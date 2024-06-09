from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
# from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from core.wqmsapi.models import CustomUser
from core.auth.serializers import PasswordResetSerializer, SetNewPasswordSerializer

class PasswordResetViewSet(viewsets.ViewSet):
    serializer_class = PasswordResetSerializer

    @action(detail=False, methods=['post'], url_path='request-password-reset-email',
            url_name='request-password-reset-email')
    def request_password_reset_email(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.data['email']
            user = CustomUser.objects.filter(email=email).first()
            if user:
                if not user.is_active:
                    return Response({'error': 'User account is not active'}, status=status.HTTP_400_BAD_REQUEST)

                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                current_site = "127.0.0.1:3000"
                relative_link = f'/password-reset/password-token-check/{uid}/{token}'
                absurl = f'http://{current_site}{relative_link}'
                email_body = f'Hi {user.username}, use the link below to reset your password\n{absurl}'
                send_mail(
                    'Reset your password',
                    email_body,
                    settings.EMAIL_HOST_USER,
                    [user.email],
                    fail_silently=False,
                )
                return Response({'detail': 'Password reset email sent.'}, status=status.HTTP_200_OK)
            return Response({'error': 'Email not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='password-token-check/(?P<uidb64>[^/.]+)/(?P<token>[^/.]+)', url_name='password-token-check')
    def password_token_check(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
            if not default_token_generator.check_token(user, token):
                raise NotFound(detail='Token is invalid or expired')
            return Response({'success': True, 'message': 'Credentials valid', 'uidb64': uidb64, 'token': token}, status=status.HTTP_200_OK)
        except Exception as e:
            raise NotFound(detail='Token is invalid or expired')

    @action(detail=False, methods=['patch'], url_path='set-new-password', url_name='set-new-password')
    def set_new_password(self, request):
        serializer = SetNewPasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'detail': 'Password reset success'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

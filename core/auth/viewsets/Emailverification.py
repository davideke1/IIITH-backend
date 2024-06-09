# views.py
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from core.auth.serializers.register import RegisterSerializer
from core.wqmsapi.models import CustomUser
from core.wqmsapi.serializers import UserSerializer
import jwt

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_active = False
            user.save()

            token = RefreshToken.for_user(user).access_token

            current_site = get_current_site(request).domain
            relativeLink = reverse('mail-verify')
            absurl = 'http://' + current_site + relativeLink + "?token=" + str(token)
            email_body = f'Hi {user.username}, use the link below to verify your email\n{absurl}'
            send_mail(
                'Verify your email',
                email_body,
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
            return Response({'detail': 'Verification email sent.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyEmail(APIView):
    serializer_class = RegisterSerializer
    def get(self, request):
        token = request.GET.get('token')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = CustomUser.objects.get(id=payload['user_id'])
            if not user.is_active:
                user.is_active = True
                user.save()
            return Response({'detail': 'Email verified successfully.'}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError:
            return Response({'error': 'Activation link expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

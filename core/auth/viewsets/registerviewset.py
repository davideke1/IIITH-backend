from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.tokens import AccessToken,BlacklistedToken,OutstandingToken
from rest_framework_simplejwt.exceptions import TokenError
from core.auth.serializers.ResendActivationLink import ResendActivationLinkSerializer
from core.auth.serializers.register import RegisterSerializer
from core.wqmsapi.models import CustomUser  # Adjust import as needed
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags



class UsersViewSet(viewsets.ViewSet):
    serializer_class = RegisterSerializer
    
    @action(detail=False, methods=['post'], url_path='register', url_name='register')
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_active = False
            user.save()

            token = RefreshToken.for_user(user).access_token

            current_site = 'http://127.0.0.1:3000'
            relative_link = f'/email-verify/{token}'
            absurl = current_site + relative_link
            # Render the HTML content for the email
            html_content = render_to_string('core/email_verification.html', {'username': user.username, 'absurl': absurl})

            # Create the plain text version of the email
            text_content = strip_tags(html_content)
            # Create the email message
            msg = EmailMultiAlternatives(
                subject='Verify your email',
                body=text_content,
                from_email=settings.EMAIL_HOST_USER,
                to=[user.email],
            )

            # Attach the HTML content
            msg.attach_alternative(html_content, "text/html")

            # Send the email
            msg.send(fail_silently=False)
            # email_body = f'Hi {user.username}, use the link below to verify your email\n{absurl}'
            # send_mail(
            #     'Verify your email',
            #     email_body,
            #     settings.EMAIL_HOST_USER,
            #     # settings.DEFAULT_FROM_EMAIL,
            #     [user.email],
            #     fail_silently=False,
            #     # connection=None
            # )
            return Response({'detail': 'Verification email sent.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='email-verify', url_name='email-verify')
    def email_verify(self, request):
        token = request.GET.get('token')
        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            user = CustomUser.objects.get(id=user_id)
            if not user.is_active:
                user.is_active = True
                user.save()

                # # Deactivate the token
                # try:
                #     outstanding_token = OutstandingToken.objects.get(token=access_token)
                #     BlacklistedToken.objects.create(token=outstanding_token)
                # except TokenError as e:
                #     return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'detail': 'Email verified successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='resend-activation-link', url_name='resend-activation-link')
    def resend_activation_link(self, request):
        serializer = ResendActivationLinkSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.data['email']
            user = CustomUser.objects.filter(email=email).first()
            if user:  # Check if user exists
                if not user.is_active:  # Only send email if user is not active
                    token = RefreshToken.for_user(user).access_token


                    current_site = '127.0.0.1:3000'
                    relative_link = f'/email-verify/'
                    # relative_link = reverse('wqmsapi:activation-email-verify')
                    absurl = 'http://' + current_site + relative_link + str(token)
                    html_content = render_to_string('core/resend_verification.html',
                                                    {'username': user.username, 'absurl': absurl})

                    # Create the plain text version of the email
                    text_content = strip_tags(html_content)
                    # Create the email message
                    msg = EmailMultiAlternatives(
                        subject='New Activation Link Request',
                        body=text_content,
                        from_email=settings.EMAIL_HOST_USER,
                        to=[user.email],
                    )

                    # Attach the HTML content
                    msg.attach_alternative(html_content, "text/html")

                    # Send the email
                    msg.send(fail_silently=False)
                    # email_body = f'Hi {user.username}, use the link below to verify your email\n{absurl}'
                    # send_mail(
                    #     'Verify your email',
                    #     email_body,
                    #     settings.EMAIL_HOST_USER,
                    #     [user.email],
                    #     fail_silently=False,
                    # )
                    return Response({'detail': 'Verification email sent.'}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'User is already active.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

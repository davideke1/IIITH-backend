from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken

class PasswordChangeViewSet(viewsets.ViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        oldpassword = request.data.get('oldpassword')
        newpassword = request.data.get('newpassword')
        confirmnewpassword = request.data.get('confirmnewpassword')

        # Server-side validation
        if not oldpassword or not newpassword or not confirmnewpassword:
            return Response({'error': 'Current password, new password, and confirmation are required.'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        if not user.check_password(oldpassword):
            return Response({'error': 'Current password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)

        if newpassword != confirmnewpassword:
            return Response({'error': 'New password and confirmation do not match.'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(newpassword)
        user.save()

        # Blacklist the current refresh token
        try:
            refresh_token = request.data.get('refresh_token')
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as e:
            return Response({'error': 'Failed.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'detail': 'Password changed successfully.'}, status=status.HTTP_200_OK)

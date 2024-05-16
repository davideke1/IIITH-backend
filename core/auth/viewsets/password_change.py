from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import check_password

class PasswordChangeViewSet(viewsets.ViewSet):
    # Specify the permission classes and HTTP methods
    permission_classes = (permissions.IsAuthenticated,)  
    http_method_names = ['post']  # Allow only POST requests

    # Define the action to handle POST requests
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
        
        return Response({'detail': 'Password changed successfully.'}, status=status.HTTP_200_OK)

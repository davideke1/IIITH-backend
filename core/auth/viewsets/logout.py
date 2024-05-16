from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.exceptions import ValidationError

class LogoutViewSet(viewsets.ViewSet):
    # authentication_classes = ()
    permission_classes = (permissions.IsAuthenticated,)  # You can temporarily change this to AllowAny for testing
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        refresh = request.data.get("refresh")
        print("Received refresh token:", refresh)  # Print the received refresh token

        if refresh is None:
            raise ValidationError({"detail": "A refresh token is required."})

        try:
            token = RefreshToken(request.data.get("refresh"))
            
            token.blacklist()
            return Response({"message": "Logged out successfully"}, status=status.HTTP_204_NO_CONTENT)
        except TokenError:
            raise ValidationError({"detail": "The refresh token is invalid."})

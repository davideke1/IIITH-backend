from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import AllowAny
from rest_framework import status, serializers
from rest_framework_simplejwt.exceptions import TokenError,InvalidToken
from core.auth.serializers import LoginSerializer

class LoginViewSet(ViewSet):
    serializer_class = LoginSerializer
    permission_classes = (AllowAny,)
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            default_errors = serializer.errors
            new_error = {}
            for field_name, field_errors in default_errors.items():
                new_error[field_name] = field_errors[0]
            return Response(new_error, status=status.HTTP_400_BAD_REQUEST)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

# # views.py
# from rest_framework import status
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework_simplejwt.tokens import RefreshToken
# from django.contrib.auth import authenticate
# from django.utils.translation import gettext_lazy as _
# from .models import CustomUser
# from .serializers import UserSerializer

# class CustomLoginView(APIView):
#     def post(self, request):
#         email = request.data.get('email')
#         password = request.data.get('password')
#         user = authenticate(request, email=email, password=password)
        
#         if user is not None:
#             if not user.is_active:
#                 return Response({'detail': _('Account is not active. Please verify your email.')}, status=status.HTTP_400_BAD_REQUEST)
            
#             refresh = RefreshToken.for_user(user)
#             return Response({
#                 'refresh': str(refresh),
#                 'access': str(refresh.access_token),
#                 'user': UserSerializer(user).data,
#             }, status=status.HTTP_200_OK)
#         return Response({'detail': _('Invalid credentials.')}, status=status.HTTP_401_UNAUTHORIZED)

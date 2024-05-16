from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import viewsets
from core.wqmsapi.serializers import SensorDataSerializer, UserSerializer
from core.wqmsapi.models import CustomUser, SensorData
from rest_framework import status

@api_view(['GET'])
def hello_world(request):
    return Response({'message': 'Hello, world i hate rajiv!'})


class UserViewSet(viewsets.ModelViewSet):
    http_method_names = {'patch', 'get'}
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer


    def get_queryset(self):
        if self.request.user.is_superuser:
            return CustomUser.objects.all()
        return CustomUser.objects.exclude(is_superuser=True)
    

    def get_object(self):
        obj= CustomUser.objects.get_object_by_public_id(self.kwargs['pk'])
        self.check_object_permissions(self.request,obj)
        return obj
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        
        # Validate the serializer
        serializer.is_valid(raise_exception=True)

        # Ensure email and username are unique
        email = serializer.validated_data.get('email')
        username = serializer.validated_data.get('username')
        if CustomUser.objects.exclude(pk=instance.pk).filter(email=email).exists():
            return Response({'error': 'Email already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        if CustomUser.objects.exclude(pk=instance.pk).filter(username=username).exists():
            return Response({'error': 'Username already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        # Save the serializer
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class SensorDataViewSet(viewsets.ModelViewSet):
    serializer_class = SensorDataSerializer

    def get_queryset(self):
        public_id = self.kwargs.get('public_id')  # Assuming you pass the public_id in the URL
        if public_id:
            return SensorData.objects.filter(user__public_id=public_id)
        elif self.request.user.is_authenticated:
            return SensorData.objects.filter(user=self.request.user)
        else:
            return SensorData.objects.none()
        

class SensorDataByLocationViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for retrieving sensor data based on latitude and longitude.
    """
    def list(self, request):
        latitude = request.query_params.get('latitude')
        longitude = request.query_params.get('longitude')

        if not latitude or not longitude:
            return Response({"error": "Latitude and longitude must be provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Find the user with the given latitude and longitude
        try:
            user = CustomUser.objects.get(latitude=latitude, longitude=longitude)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found for the given latitude and longitude"}, status=status.HTTP_404_NOT_FOUND)

        # Retrieve sensor data for the user
        sensor_data = SensorData.objects.filter(user=user)

        # Serialize the sensor data
        serializer = SensorDataSerializer(sensor_data, many=True)

        return Response(serializer.data)

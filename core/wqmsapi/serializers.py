from core.wqmsapi.models import CustomUser, SensorData
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='public_id',
                               read_only=True, format='hex')
    class Meta:
        model = CustomUser
        fields = ['id', 'username','first_name','last_name', 'email', 'is_active', 'created', 'updated']
        read_only_fields = ['is_active', 'created', 'updated']
        


class SensorDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorData
        fields = '__all__'

from core.wqmsapi.models import Feedback, Notification, CustomUser
from rest_framework import serializers


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'subtitle', 'status']


class CustomUserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='public_id',
                               read_only=True, format='hex')

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'thinkspeak_api_key', 'latitude', 'longitude', 'is_active']


class UserListSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='public_id',
                               read_only=True, format='hex')

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'is_active', 'is_superuser', 'is_staff']
        read_only_fields = ['is_active', 'is_superuser', 'is_staff']

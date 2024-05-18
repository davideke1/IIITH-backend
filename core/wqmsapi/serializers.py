from django.utils import timezone

from core.wqmsapi.models import ActivityLog, CustomUser, Feedback, SensorData,Notification
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='public_id',
                               read_only=True, format='hex')
    class Meta:
        model = CustomUser
        fields = ['id', 'username','first_name','last_name', 'email','role', 'is_active']
        read_only_fields = ['is_active','role']
        
   
# Remember to remove the user lat and long in the serializers
class DateTimeFieldSerializer(serializers.DateTimeField):
    def to_representation(self, value):
        value = timezone.localtime(value)
        return value.strftime('%Y-%m-%d %H:%M:%S')


class SensorDataSerializer(serializers.ModelSerializer):
    timestamp = DateTimeFieldSerializer()
    class Meta:
        model = SensorData
        fields = '__all__'


class SensorDataExportSerializer(serializers.ModelSerializer):
    timestamp = DateTimeFieldSerializer()

    class Meta:
        model = SensorData
        fields = ['temperature', 'humidity', 'PH', 'tds', 'do', 'timestamp']


class UserLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id','email','username','latitude', 'longitude']
        
    
class PublishedNotificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'subtitle']
    
    def to_representation(self, instance):
        if instance.status != Notification.PUBLISHED:
            return None
        return super().to_representation(instance)
    
    
class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = '__all__'
        
        
class UsernameFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username']

class UserFeedbackSerializer(serializers.ModelSerializer):
    user = UsernameFeedbackSerializer(read_only=True)

    class Meta:
        model = Feedback
        fields = ['id', 'user', 'message', 'created_at']
        read_only_fields = ['created_at']
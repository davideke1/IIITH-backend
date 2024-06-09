from django.urls import re_path,path
from .consumers import AdminSensorDataConsumer, SensorDataConsumer, SensorDataAdminConsumer, AlertConsumer, WQIConsumer

websocket_urlpatterns = [
    re_path(r'ws/sensor-data/user/(?P<public_id>\w+)/$', SensorDataConsumer.as_asgi()),
    re_path(r'ws/user-sensor-data/admin/(?P<latitude>[-+]?\d*\.\d+|\d+)/(?P<longitude>[-+]?\d*\.\d+|\d+)/$', AdminSensorDataConsumer.as_asgi()),
    re_path(r'ws/admin/sensor-data/', SensorDataAdminConsumer.as_asgi()),
    re_path(r'ws/admin/wqi/$', WQIConsumer.as_asgi()),
    path('ws/alerts/', AlertConsumer.as_asgi()),
]

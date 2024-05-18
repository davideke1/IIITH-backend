import json
import uuid

from django.test import Client
from channels.testing import WebsocketCommunicator
from core.wqmsapi.models import CustomUser
from django.test import TestCase
from core.consumers import SensorDataAdminConsumer, SensorDataConsumer
from core.routing import websocket_urlpatterns
from channels.routing import URLRouter
from asgiref.sync import sync_to_async

class ConsumerTestCase(TestCase):
    async def test_sensor_data_admin_consumer_permissions(self):
        # Create an admin user
        admin_user = await sync_to_async(CustomUser.objects.create_superuser)(username='admin', email='admin@admin.com',password='testpass')

        # Create a non-admin user
        regular_user = await sync_to_async(CustomUser.objects.create_user)(username='regular', email='regular@gmail.com',password='testpass')

        # Test that the admin user can connect
        communicator = WebsocketCommunicator(SensorDataAdminConsumer.as_asgi(), "/ws/admin/sensor-data/")
        communicator.scope["custom_user"] = admin_user
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        await communicator.disconnect()

        # Test that the non-admin user cannot connect
        communicator = WebsocketCommunicator(SensorDataAdminConsumer.as_asgi(), "/ws/admin/sensor-data/")
        communicator.scope["custom_user"] = regular_user
        connected, _ = await communicator.connect()
        self.assertFalse(connected)
        await communicator.disconnect()

    async def test_sensor_data_consumer_permissions(self):
        # Create a regular user
        regular_user = await sync_to_async(CustomUser.objects.create_user)(username='regular',
                                                                           email='regular@gmail.com',
                                                                           password='testpass')
        # Generate a valid UUID for public_id
        public_id = str(uuid.uuid4())

        # Test that the regular user can connect
        communicator = WebsocketCommunicator(SensorDataConsumer.as_asgi(), f"/ws/sensor-data/{public_id}/")
        communicator.scope["custom_user"] = regular_user
        communicator.scope["url_route"] = {"kwargs": {"public_id": public_id}}
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        await communicator.disconnect()

        # Test that an anonymous user cannot connect
        communicator = WebsocketCommunicator(SensorDataConsumer.as_asgi(), f"/ws/sensor-data/{public_id}/")
        communicator.scope["url_route"] = {"kwargs": {"public_id": public_id}}
        connected, _ = await communicator.connect()
        self.assertFalse(connected)
        await communicator.disconnect()
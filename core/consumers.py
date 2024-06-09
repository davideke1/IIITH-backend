import json
from decimal import Decimal
from datetime import datetime, timedelta
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.db.models.functions import Cast
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser
from core.wqmsapi.models import SensorData, CustomUser
from asgiref.sync import sync_to_async
import logging
import asyncio
from django.db.models import Max, Avg, FloatField

logger = logging.getLogger(__name__)


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(DecimalEncoder, self).default(obj)


class SensorDataConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.public_id = self.scope['url_route']['kwargs']['public_id']
        self.group_name = f'sensor_data_{self.public_id}'

        # Check if the user is authenticated
        # if 'custom_user' in self.scope and not isinstance(self.scope['custom_user'], AnonymousUser):
        # if not isinstance(self.scope['user'], AnonymousUser):
        # self.group_name = "dashboard"
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()
        print(self.group_name)
        print(f"WebSocket connected: {self.channel_name}")

        # Send previous data when a new client connects
        await self.send_previous_sensor_data()
        # else:
        #     await self.close(code=403)  # Close the connection if the user is not authenticated

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        print(f"WebSocket disconnected: {self.channel_name}")

    async def receive(self, text_data):
        # data = json.loads(text_data)
        # await self.channel_layer.group_send(
        #     self.group_name,
        #     {
        #         'type': 'send_sensor_data',
        #         'data': [data]  # Wrap the single object in a list
        #     }
        # )
        pass

    async def send_sensor_data(self, event):
        data = event['data']
        # print("Received new sensor data:", data) 
        await self.send(text_data=json.dumps(data, cls=DecimalEncoder))
        # print("Sensor data sent to consumer")

    async def send_previous_sensor_data(self):
        previous_data = await self.get_previous_sensor_data()
        await self.send(text_data=json.dumps(previous_data, cls=DecimalEncoder))

    @sync_to_async
    def get_previous_sensor_data(self):
        previous_data = SensorData.objects.filter(user__public_id=self.public_id).values('temperature', 'humidity',
                                                                                         'PH', 'tds', 'do',
                                                                                         'timestamp')[:50]
        return list(previous_data)


#
# class SensorDataAdminConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         await self.accept()
#         self.send_task = asyncio.create_task(self.send_latest_sensor_data())
#
#     async def disconnect(self, close_code):
#         self.send_task.cancel()
#
#     async def send_latest_sensor_data(self):
#         while True:
#             try:
#                 latest_data = await self.get_latest_sensor_data()
#                 await self.send(text_data=json.dumps(latest_data))
#             except Exception as e:
#                 print(f"Error fetching sensor data: {e}")
#             await asyncio.sleep(5)  # Adjust the interval as needed
#
#     @sync_to_async
#     def get_latest_sensor_data(self):
#         parameters = ['PH', 'temperature', 'tds', 'do', 'humidity']
#         latest_data = {}
#
#         # Get the latest data
#         for param in parameters:
#             sensor_data = SensorData.objects.all().order_by('-timestamp').first()
#             value = getattr(sensor_data, param, None)
#             if value:
#                 latest_data[param] = {
#                     param: float(value),  # Convert Decimal to float
#                     "timestamp": sensor_data.timestamp.isoformat()  # Use actual timestamp
#                 }
#
#         # Optionally, send aggregated data over a short period (e.g., last 5 minutes)
#         end_time = datetime.now()
#         start_time = end_time - timedelta(seconds=45)
#         for param in parameters:
#             avg_data = SensorData.objects.filter(
#                 timestamp__range=(start_time, end_time)
#             ).aggregate(average_value=Cast(Avg(param), output_field=FloatField()))
#             if avg_data['average_value'] is not None:
#                 latest_data[f"{param}_avg"] = {
#                     "average": float(avg_data['average_value']),  # Convert Decimal to float
#                     "timestamp": end_time.isoformat()
#                 }
#
#         return latest_data


class SensorDataAdminConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Check if the user is authenticated and has the required permissions
        # if 'custom_user' in self.scope and not isinstance(self.scope['custom_user'], AnonymousUser) and self.scope['custom_user'].is_staff:
        await self.accept()
        self.send_task = asyncio.create_task(self.send_average_sensor_data())
        print(f"WebSocket connected admin")

    async def disconnect(self, close_code):
        # if hasattr(self, 'send_task'):
        self.send_task.cancel()

    async def send_average_sensor_data(self):
        while True:
            try:
                average_data = await self.get_average_sensor_data()
                await self.send(text_data=json.dumps(average_data, default=self.json_serial))
            except Exception as e:
                print(f"Error fetching sensor data: {e}")
            await asyncio.sleep(10)  # Send data every minute for testing purposes

    @sync_to_async
    def get_average_sensor_data(self):
        parameters = ['PH', 'temperature', 'tds', 'do', 'humidity']
        end_time = timezone.localtime(timezone.now())
        start_time = end_time - timedelta(days=1)

        average_data = {param: {} for param in parameters}

        for param in parameters:
            data = SensorData.objects.filter(timestamp__range=(start_time, end_time)).values('timestamp', param)

            # Group data by 5-minute intervals
            interval_data = {}
            for entry in data:
                timestamp = entry['timestamp']
                interval_start = timestamp.replace(minute=(timestamp.minute // 5) * 5, second=0, microsecond=0)
                if interval_start not in interval_data:
                    interval_data[interval_start] = []
                if entry[param] is not None:
                    interval_data[interval_start].append(entry[param])

            for interval_start, values in interval_data.items():
                if values:
                    average_value = sum(values) / len(values)
                    average_data[param][interval_start.isoformat()] = average_value

        return average_data

    def json_serial(self, obj):
        if isinstance(obj, (datetime, Decimal)):
            return str(obj)
        raise TypeError("Type not serializable")


class AlertConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("alerts", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("alerts", self.channel_name)

    async def send_alert(self, event):
        await self.send(text_data=json.dumps(event["message"]))


class AdminSensorDataConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.latitude = self.scope['url_route']['kwargs']['latitude']
        self.longitude = self.scope['url_route']['kwargs']['longitude']
        self.group_name = f'sensor_data_admin_{self.latitude}_{self.longitude}'

        # Check if the user is authenticated and has the required permissions
        # if 'custom_user' in self.scope and not isinstance(self.scope['custom_user'], AnonymousUser) and self.scope['custom_user'].is_staff:
        # Join room group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()
        self.send_task = asyncio.create_task(self.send_user_reading())
        # else:
        #     await self.close(
        #         code=403)  # Close the connection if the user is not authenticated or doesn't have admin permissions

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        self.send_task.cancel()

    async def send_user_reading(self):
        while True:
            try:
                user_reading = await self.get_sensor_data(self.latitude, self.longitude)
                await self.send(text_data=json.dumps(user_reading, cls=DecimalEncoder))
            except Exception as e:
                print(f"Error fetching sensor data: {e}")
            await asyncio.sleep(5)

    @sync_to_async()
    def get_sensor_data(self, latitude, longitude):
        try:
            # Fetch user based on latitude and longitude
            user = CustomUser.objects.get(latitude=latitude, longitude=longitude)

            # Fetch the most recent sensor data for the user
            recent_sensor_data = SensorData.objects.filter(user=user).order_by('-timestamp').first()

            if recent_sensor_data:
                return {
                    'timestamp': recent_sensor_data.timestamp,
                    'temperature': recent_sensor_data.temperature,
                    'humidity': recent_sensor_data.humidity,
                    'ph': recent_sensor_data.PH,
                    'tds': recent_sensor_data.tds,
                    'do': recent_sensor_data.do
                }
            else:
                return {
                    'error': 'No sensor data found for the user'
                }
        except CustomUser.DoesNotExist:
            return {
                'error': 'User not found for the given coordinates'
            }


class WQIConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # print("Connection scope:", self.scope)
        #
        # user = self.scope.get('user')
        # print(f"User in scope: {user}")
        # print(f"User is authenticated: {user.is_authenticated}")
        # print(f"User is staff: {user.is_staff}")
        # # Check if the user is authenticated and has the required permissions
        # if 'user' in self.scope and not isinstance(self.scope['user'], AnonymousUser) and self.scope['user'].is_staff:
        await self.accept()
        print('connected')
        self.send_task = asyncio.create_task(self.send_wqi_data())
        # else:
        #     await self.close(code=403)

    async def disconnect(self, code):
        self.send_task.cancel()
        # await super().disconnect(code)
        print('disconnected')

    async def send_wqi_data(self):
        while True:
            try:
                wqi_data = await self.calculate_wqi()
                await self.send(text_data=json.dumps(wqi_data, cls=DecimalEncoder))
            except Exception as e:
                print(f"Error calculating WQI: {e}")
            await asyncio.sleep(5)

    @sync_to_async
    def calculate_wqi(self):
        parameters = ['PH', 'temperature', 'tds', 'do', 'turbidity']
        users = SensorData.objects.values_list('user__username', flat=True).distinct()
        wqi_data = []

        for user in users:
            latest_entries = SensorData.objects.filter(user__username=user).order_by('-timestamp').first()
            if not latest_entries:
                continue

            wqi = self.calculate_user_wqi(latest_entries)
            wqi_data.append({
                'user': user,
                'wqi': wqi,
                'timestamp': latest_entries.timestamp.isoformat()
            })

        return wqi_data

    def calculate_user_wqi(self, data):
        # Example WQI calculation
        # The WQI formula depends on the specific parameters and their thresholds
        # Here, a simple weighted average is used for demonstration

        weights = {'PH': Decimal('0.2'), 'temperature': Decimal('0.2'), 'tds': Decimal('0.2'), 'do': Decimal('0.2'),
                   'humidity': Decimal('0.2')}
        wqi = Decimal(0)

        for param, weight in weights.items():
            value = getattr(data, param)
            if value is not None:
                # Normalize value to a score (for simplicity, assume all values are between 0-100)
                normalized_value = value / 100
                wqi += normalized_value * weight

        return wqi * Decimal(100)  # Scale to 0-100

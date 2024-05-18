from django.core.management.base import BaseCommand
from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
from ...wqmsapi.models import CustomUser, SensorData
import random
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
import logging
import time
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Configure logging
logger = logging.getLogger(__name__)

executors = {
    'default': ThreadPoolExecutor(20),
    'processpool': ProcessPoolExecutor(5)
}

job_defaults = {
    'coalesce': False,
    'max_instances': 5,
}

class Command(BaseCommand):
    help = 'Generate and store sensor data at regular intervals'

    def handle(self, *args, **options):
        scheduler = BackgroundScheduler(executors=executors, job_defaults=job_defaults)

        def generate_and_store_sensor_data(user_id):
            user = CustomUser.objects.get(public_id=user_id)
            timestamp = timezone.now()
            temperature = round(random.uniform(20, 30), 2)
            humidity = round(random.uniform(40, 80), 2)
            pH = round(random.uniform(6.5, 7.5), 2)
            tds = round(random.uniform(200, 500), 2)
            do = round(random.uniform(5, 10), 2)
            sensor_data = SensorData.objects.create(
                user=user,
                temperature=temperature,
                humidity=humidity,
                PH=pH,
                tds=tds,
                do=do,
                timestamp=timestamp
            )
            sensor_data.save()

            # # Send the data to the WebSocket group
            # channel_layer = get_channel_layer()
            # if channel_layer:
            #     user_public_id =user.public_id.hex
            #     group_name = f'sensor_data_{user_public_id}'
            #     async_to_sync(channel_layer.group_send)(
            #         group_name,
            #         {
            #             'type': 'send_sensor_data',
            #             'data': {
            #                 'temperature': str(sensor_data.temperature),
            #                 'humidity': str(sensor_data.humidity),
            #                 'PH': str(sensor_data.PH),
            #                 'tds': str(sensor_data.tds),
            #                 'do': str(sensor_data.do),
            #                 'timestamp': sensor_data.timestamp.isoformat(),
            #             }
            #         }
            #     )
            #     print(f"Data sent to group {group_name}")

        def get_user_public_ids():
            users = CustomUser.objects.all()
            public_ids = [user.public_id for user in users]
            return public_ids

        public_ids = get_user_public_ids()

        for public_id in public_ids:
            scheduler.add_job(
                generate_and_store_sensor_data,
                'interval',
                seconds=5,
                args=[public_id]
            )
        scheduler.start()
        self.stdout.write(self.style.SUCCESS("Scheduler started. Press Ctrl+C to exit."))

        try:
            while True:
                time.sleep(2)
        except (KeyboardInterrupt, SystemExit):
            scheduler.shutdown()
            self.stdout.write(self.style.SUCCESS("Scheduler stopped."))

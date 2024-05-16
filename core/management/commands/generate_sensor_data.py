from django.core.management.base import BaseCommand
from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
from ...wqmsapi.models import CustomUser, SensorData
import random

class Command(BaseCommand):
    help = 'Generate and store sensor data at regular intervals'

    def handle(self, *args, **options):
        scheduler = BackgroundScheduler()

        def generate_and_store_sensor_data(user_id):
            user = CustomUser.objects.get(public_id=user_id)
            timestamp = timezone.now()  # Generate a single timestamp
            temperature = round(random.uniform(20, 30), 2)
            humidity = round(random.uniform(40, 70), 2)
            pH = round(random.uniform(6.5, 7.5), 2)
            tds = round(random.uniform(200, 500), 2)
            do = round(random.uniform(5, 10), 2)
            SensorData.objects.create(
                user=user,
                temperature=temperature,
                humidity=humidity,
                PH=pH,
                tds=tds,
                do=do,
                timestamp=timestamp  # Use the single timestamp
            )

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
                args=[public_id]  # Pass user_id as an argument
            )

        # Start the scheduler
        scheduler.start()

        # Wait for user input to stop the scheduler
        input("Press any key to stop the scheduler...")

        # Shutdown the scheduler
        scheduler.shutdown()

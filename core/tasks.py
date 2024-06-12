from django.utils import timezone
from celery import shared_task
import requests
from django.utils.dateparse import parse_datetime
from core.wqmsapi.models import SensorData, CustomUser
import logging
from django.db import transaction

logger = logging.getLogger(__name__)

@shared_task
def fetch_and_store_data():
    logger.info("Task fetch_and_store_data started")
    active_users = CustomUser.objects.filter(
        is_active=True,
        role='user'  # Add role filter
    ).exclude(
        thinkspeak_api_key__isnull=True
    )

    for user in active_users:
        url = f'https://api.thingspeak.com/channels/2392715/feeds.json?api_key={user.thinkspeak_api_key}&results=1'
        response = requests.get(url)
        logger.info(f"Fetching data for user {user.username}: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            feeds = data.get('feeds', [])
            for feed in feeds:
                logger.info(f"Fetched data for user {user.username}: {feed}")
                timestamp = parse_datetime(feed.get('created_at')) or timezone.now()
                try:
                    with transaction.atomic():  # Ensure atomicity within each feed update
                        sensor_data, created = SensorData.objects.update_or_create(
                            user=user,
                            timestamp=timestamp,
                            defaults={
                                'temperature': float(feed.get('field1', 0)),
                                'humidity': float(feed.get('field4', 0)),
                                'PH': float(feed.get('field3', 0)),
                                'tds': float(feed.get('field2', 0)),
                                'do': float(feed.get('field5', 0)),
                            }
                        )
                        logger.info(f"Data {'created' if created else 'updated'} for user {user.username} at {timestamp}")
                except Exception as e:
                    logger.error(f"Error saving data for user {user.username}: {e}")
        elif response.status_code == 304:
            logger.info(f"No new data available for user {user.username}.")
        else:
            logger.error(f"Failed to fetch data for user {user.username}: {response.status_code}")
    logger.info("Task fetch_and_store_data finished")


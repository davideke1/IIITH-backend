from .base import *
import os
from dotenv import load_dotenv


load_dotenv(os.path.join(BASE_DIR, '.env.dev'))

DEBUG = os.environ.get('DEBUG')
# Raises Django's ImproperlyConfigured
# exception if SECRET_KEY not in os.environ
SECRET_KEY = os.environ.get('SECRET_KEY')
print(SECRET_KEY)

ADMINS = [
 ('Ekechukwu D', 'ekechukwudavid@gmail.com'),
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB'),
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': 'db',
        'PORT': 5432,
        'ATOMIC_REQUESTS': True,
        'OPTIONS': {
            'options': '-c timezone=Asia/Kolkata'
        },
    }
}
REDIS_URL = 'redis://redis:6379/0'
# CHANNEL LAYERS
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [REDIS_URL],  # Update this line to use the REDIS_URL
        },
    },
}



CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND',
                                       'db+postgresql://postgres:postgres@db:5432/postgres')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_TASK_TRACK_STARTED = True

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
from .base import *
DEBUG= True
from dotenv import load_dotenv

load_dotenv(os.path.join(BASE_DIR, '.env'))
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '10.2.136.64','172.26.224.67']
# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DATABASE_NAME'),
        'USER': os.environ.get('DATABASE_USER'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD'),
        'HOST': os.environ.get('DATABASE_HOST'),
        'PORT': os.environ.get('DATABASE_PORT'),
        'ATOMIC_REQUESTS': True,
        'OPTIONS': {
            'options': '-c timezone=Asia/Kolkata'
        },
    }
}


CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            # "hosts": [os.getenv('REDIS_URL', 'redis://localhost:6379')],
            "hosts": [("127.0.0.1", 6379)]
        },
    },
}


CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND',
                                       'db+postgresql://postgres:Daviduzoma_1@localhost:5433/IIITHWQMSAPI')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_TASK_TRACK_STARTED = True
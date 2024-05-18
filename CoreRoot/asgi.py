import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
# from core.wqmsapi.models import CustomUser
# from core.jwt_auth_middleware import JWTAuthMiddleware

# Set the default settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', os.getenv('DJANGO_SETTINGS_MODULE', 'CoreRoot.settings'))

django_asgi_app = get_asgi_application()

from core.consumers import SensorDataConsumer,SensorDataAdminConsumer,AdminSensorDataConsumer,WQIConsumer

from core import routing
application = ProtocolTypeRouter({
    "http": django_asgi_app,

    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(routing.websocket_urlpatterns)
        )
    ),
})

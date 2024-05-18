
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from CoreRoot.health_checks import health_check

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(('core.routers', 'core'), namespace='wqmsapi')),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "docs/", SpectacularSwaggerView.as_view(),
        name="swagger-ui"
    ),
    path('health/', health_check, name='health_check'),
]

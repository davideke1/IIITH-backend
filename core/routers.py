from rest_framework.routers import SimpleRouter
from core.wqmsapi.views import SensorDataByLocationViewSet, SensorDataViewSet, UserViewSet
from core.auth.viewsets import RegisterViewSet, LoginViewSet, RefreshViewSet,LogoutViewSet,PasswordChangeViewSet
from core.wqmsapi import views
from django.urls import path

routes = SimpleRouter()
#authentication
routes.register(r'password-change', PasswordChangeViewSet, basename='password-change')
routes.register(r'user-auth/register',RegisterViewSet, basename='user-auth-register')
routes.register(r'user-auth/login', LoginViewSet, basename='user-auth-login')
routes.register(r'user-auth/refresh', RefreshViewSet, basename='user-auth-refresh')
routes.register(r'user-auth/logout',LogoutViewSet, basename='user-auth-logout')
#features
routes.register(r'sensordata/(?P<public_id>[^/.]+)', SensorDataViewSet, basename='sensordata')
routes.register(r'sensor-data-by-location', SensorDataByLocationViewSet, basename='sensor-data-by-location')
#user
routes.register(r'user', UserViewSet, basename='user')
urlpatterns = [
    *routes.urls,
    path('hello-world/', views.hello_world, name='hello_world'),
]

from rest_framework.routers import SimpleRouter
# from core.admindashboard.views import DashboardViewSet
from CoreRoot.health_checks import health_check
from core.admindashboard.views import AdminViewSet, DashboardViewSet, UserListViewSet, \
    UserManagementViewSet, NotificationViewSet, HistorySensorDataViewSet
from core.auth.viewsets.Emailverification import RegisterView, VerifyEmail
from core.auth.viewsets.PAsswordReset import PasswordResetViewSet
from core.auth.viewsets.adminlogin import AdminLoginViewSet
from core.auth.viewsets.registerviewset import UsersViewSet
from core.wqmsapi.views import ActivityLogViewSet, PublishedNotificationsViewSet, UserLocationViewSet, FeedbackViewSet, \
    UserViewSet, \
    UserSensorDataViewSet, check_authentication
from core.auth.viewsets import RegisterViewSet, LoginViewSet, RefreshViewSet, LogoutViewSet, PasswordChangeViewSet
from core.wqmsapi import views
from django.urls import path

routes = SimpleRouter()
# authentication
routes.register(r'password-change', PasswordChangeViewSet, basename='password-change')
routes.register(r'user-auth/register', RegisterViewSet, basename='user-auth-register')
routes.register(r'user-auth/login', LoginViewSet, basename='user-auth-login')
routes.register(r'user-auth/refresh', RefreshViewSet, basename='user-auth-refresh')
routes.register(r'user-auth/logout', LogoutViewSet, basename='user-auth-logout')
# features
# routes.register(r'sensordata/(?P<public_id>[^/.]+)', SensorDataViewSet, basename='sensordata')
# routes.register(r'sensor-data-by-location', SensorDataByLocationViewSet, basename='sensor-data-by-location')
# routes.register(r'user-locations', UserLocationViewSet, basename='user-location')
routes.register(r'notifications', PublishedNotificationsViewSet, basename='Notification')
routes.register(r'activations', UsersViewSet, basename='activation')
routes.register(r'password-reset', PasswordResetViewSet, basename='password-reset')
routes.register(r'user-sensor-data', UserSensorDataViewSet, basename='user-sensor-data')
# routes.register(r'user-feedback', FeedbackViewSet, basename='feedback')
# admin
routes.register(r'dashboard', DashboardViewSet, basename='dashboard')
routes.register(r'adminlogin', AdminLoginViewSet, basename='adminlogin')
# routes.register(r'sensordata', SensorDataViewSet, basename='sensordata')
routes.register(r'activities', ActivityLogViewSet, basename="user-activities")
routes.register(r'admin', AdminViewSet, basename='admin')
# routes.register(r'notifications', NotificationViewSet, basename='notifications')
routes.register(r'feedback', FeedbackViewSet, basename='feedback')
routes.register(r'user_management', UserManagementViewSet, basename='user_management')
routes.register(r'user_list', UserListViewSet, basename='user_list')
routes.register(r'notificationadmin', NotificationViewSet, basename='adminnotification')
routes.register(r'history-sensor-data', HistorySensorDataViewSet, basename='history-sensor-data')
routes.register(r'sensor-locations', UserLocationViewSet, basename='sensor-locations')
# user
routes.register(r'user', UserViewSet, basename='user')
urlpatterns = [
    *routes.urls,
    path('hello-world/', views.hello_world, name='hello_world'),
    path('register/', RegisterView.as_view(), name='register'),
    path('email-verify/', VerifyEmail.as_view(), name='mail-verify'),
    path('check-auth/', check_authentication, name='check_auth'),
    # path('health/', health_check, name='health_check'),
    # path('historical-data/', HistoricalDataView.as_view(), name='historical-data'),
    # path('export/<str:data_type>/', export_data),
]

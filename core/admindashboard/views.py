from rest_framework import viewsets, permissions, pagination
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils.dateparse import parse_datetime
from rest_framework.views import APIView

from core.admindashboard.serializers import NotificationSerializer, CustomUserSerializer, UserListSerializer, \
    FeedbackSerializer
from core.wqmsapi.models import CustomUser, SensorData, Notification, ActivityLog, Feedback
from core.wqmsapi.serializers import UserSerializer, SensorDataSerializer, ActivityLogSerializer
import csv
import pandas as pd
from django.http import HttpResponse, JsonResponse
from rest_framework import status
from datetime import datetime, timedelta
from django.utils.dateparse import parse_date
from django.core.paginator import Paginator


class HistorySensorDataViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAdminUser]
    queryset = SensorData.objects.all()
    serializer_class = SensorDataSerializer

    @action(detail=False, methods=['get'])
    def historical_data(self, request):
        username = request.query_params.get('username')
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')

        if not username:
            return Response({'error': 'username query parameter is required'}, status=400)

        try:
            # Check for missing username first
            if not username:
                return Response({'error': 'Missing username parameter'}, status=400)

            # Fetch sensor data for the user
            user_sensor_data = SensorData.objects.filter(user__username=username).order_by('timestamp')

            # Check for empty data and handle accordingly
            if not user_sensor_data.exists():  # Use `exists()` for clarity
                return Response({'message': 'No data found for the specified user'}, status=404)

            # Date filtering logic (optional, similar to previous responses)
            if request.GET.get('start_date'):
                start_date = parse_date(request.GET['start_date'])
                if request.GET.get('end_date'):
                    end_date = parse_date(request.GET['end_date'])
                else:
                    end_date = datetime.now()
            else:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=3)

            user_sensor_data = user_sensor_data.filter(timestamp__range=[start_date, end_date])

            serializer = SensorDataSerializer(user_sensor_data, many=True)

            return Response(serializer.data)

        except (SensorData.DoesNotExist, ValueError, TypeError) as e:
            # Handle potential exceptions more comprehensively
            error_message = str(e)  # Extract the error message for clarity
            if isinstance(e, (ValueError, TypeError)):
                error_message = f'Invalid date format: {error_message}'
            return Response({'error': error_message}, status=400)


class DashboardViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAdminUser]

    @action(detail=False, methods=['get'])
    def summary(self, request):
        users_count = CustomUser.objects.count()
        active_users_count = CustomUser.objects.filter(is_active=True).count()
        notifications_count = Notification.objects.count()
        activities_count = ActivityLog.objects.count()

        summary = {
            'users_count': users_count,
            'active_users_count': active_users_count,
            'notifications_count': notifications_count,
            'activities_count': activities_count,
        }
        return Response(summary)


class AdminViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAdminUser]

    @action(detail=False, methods=['get'])
    def export_users(self, request):
        users = CustomUser.objects.all()
        serializer = UserSerializer(users, many=True)
        df = pd.DataFrame(serializer.data)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=users.csv'
        df.to_csv(path_or_buf=response, index=False)
        return response

    @action(detail=False, methods=['get'])
    def export_sensor_data(self, request):
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')

        start_date = None if start_date_str == "null" else start_date_str
        end_date = None if end_date_str == "null" else end_date_str

        sensor_data = SensorData.objects.all()

        if start_date and end_date:
            start_date = parse_datetime(start_date + 'T00:00:00Z')  # Assuming the format is YYYY-MM-DD
            end_date = parse_datetime(end_date + 'T23:59:59Z')
            sensor_data = sensor_data.filter(timestamp__range=[start_date, end_date])

        filename = "sensor_data"
        if start_date:
            filename += f"_from_{start_date.date()}"
        if end_date:
            filename += f"_to_{end_date.date()}"
        filename += ".csv"
        serializer = SensorDataSerializer(sensor_data, many=True)
        df = pd.DataFrame(serializer.data)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        df.to_csv(path_or_buf=response, index=False)
        return response

    @action(detail=False, methods=['get'])
    def export_user_sensor_data(self, request):
        username = request.query_params.get('username')
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')

        start_date = None if start_date_str == "null" else start_date_str
        end_date = None if end_date_str == "null" else end_date_str

        user_sensor_data = SensorData.objects.select_related('user').all()
        # print(user_sensor_data.count())
        if username:
            user_sensor_data = user_sensor_data.filter(user__username=username)
        # print(user_sensor_data.count())
        if start_date and end_date:
            start_date = parse_datetime(start_date + 'T00:00:00Z')  # Assuming the format is YYYY-MM-DD
            end_date = parse_datetime(end_date + 'T23:59:59Z')  # End of day
            # print(start_date,end_date)
            user_sensor_data = user_sensor_data.filter(timestamp__range=[start_date, end_date])
        # print(user_sensor_data.count())
        if not user_sensor_data.exists():
            return JsonResponse({"message": "No data found for the specified criteria."}, status=404)

        filename = f"{username}_sensor_data"
        if start_date:
            filename += f"_from_{start_date.date()}"
        if end_date:
            filename += f"_to_{end_date.date()}"
        filename += ".csv"

        data = [
            {
                'user_id': sensor_data.user.id,
                'user_username': sensor_data.user.username,
                'temperature': sensor_data.temperature,
                'humidity': sensor_data.humidity,
                'PH': sensor_data.PH,
                'tds': sensor_data.tds,
                'do': sensor_data.do,
                'timestamp': sensor_data.timestamp
            }
            for sensor_data in user_sensor_data
        ]
        df = pd.DataFrame(data)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        df.to_csv(path_or_buf=response, index=False)
        return response

    @action(detail=False, methods=['get'])
    def export_notifications(self, request):
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')

        start_date = None if start_date_str == "null" else start_date_str
        end_date = None if end_date_str == "null" else end_date_str

        notifications = Notification.objects.all()

        if start_date and end_date:
            start_date = parse_datetime(start_date + 'T00:00:00Z')  # Assuming the format is YYYY-MM-DD
            end_date = parse_datetime(end_date + 'T23:59:59Z')
            notifications = notifications.filter(created_at__range=[start_date, end_date])

        if not notifications.exists():
            return HttpResponse("No data found for the specified criteria.", status=404)

        serializer = NotificationSerializer(notifications, many=True)
        df = pd.DataFrame(serializer.data)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=notifications.csv'
        df.to_csv(path_or_buf=response, index=False)
        return response

    @action(detail=False, methods=['get'])
    def export_activities(self, request):
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')

        start_date = None if start_date_str == "null" else start_date_str
        end_date = None if end_date_str == "null" else end_date_str

        activities = ActivityLog.objects.all()

        if start_date and end_date:
            start_date = parse_datetime(start_date + 'T00:00:00Z')  # Assuming the format is YYYY-MM-DD
            end_date = parse_datetime(end_date + 'T23:59:59Z')
            activities = activities.filter(created_at__range=[start_date, end_date])

        if not activities.exists():
            return HttpResponse("No data found for the specified criteria.", status=404)

        serializer = ActivityLogSerializer(activities, many=True)
        df = pd.DataFrame(serializer.data)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=activities.csv'
        df.to_csv(path_or_buf=response, index=False)
        return response


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit objects.
    """

    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the admin user.
        return request.user and request.user.is_staff


class NotificationPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = NotificationPagination

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class FeedbackViewSet(viewsets.ModelViewSet):
#     permission_classes = [permissions.IsAdminUser]
#     queryset = Feedback.objects.all()
#     serializer_class = FeedbackSerializer


class UserManagementViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = CustomUserSerializer
    lookup_field = 'public_id'

    @action(detail=True, methods=['put'])
    def update_thinkspeak_info(self, request, public_id=None):
        user = CustomUser.objects.get(public_id=public_id)
        user.thinkspeak_api_key = request.data.get('thinkspeak_api_key', user.thinkspeak_api_key)
        user.latitude = request.data.get('latitude', user.latitude)
        user.longitude = request.data.get('longitude', user.longitude)
        user.save()
        return Response({'status': 'User updated'})
    #
    # @action(detail=False, methods=['put'])
    # def bulk_update(self, request):
    #     user_ids = request.data.get('user_ids', [])
    #     think_speak_api_key = request.data.get('thinkspeak_api_key')
    #     latitude = request.data.get('latitude')
    #     longitude = request.data.get('longitude')
    #     CustomUser.objects.filter(id__in=user_ids).update(thinkspeak_api_key=think_speak_api_key, latitude=latitude,
    #                                                       longitude=longitude)
    #     return Response({'status': 'Users updated'})

    @action(detail=False, methods=['get'])
    def list_active_users(self, request):
        page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 10)

        active_users = CustomUser.objects.filter(is_active=True).exclude(is_superuser=True)
        paginator = Paginator(active_users, page_size)
        page_obj = paginator.get_page(page)

        serializer = CustomUserSerializer(page_obj, many=True)
        # print(serializer.data)
        return Response({
            'total_pages': paginator.num_pages,
            'current_page': page_obj.number,
            'total_users': paginator.count,
            'results': serializer.data
        })


    @action(detail=False, methods=['get'])
    def list_all_active_users(self, request):
        active_users = CustomUser.objects.filter(is_active=True).exclude(is_superuser=True)
        serializer = CustomUserSerializer(active_users, many=True)
        return Response(serializer.data)


class UserPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class UserListViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAdminUser]
    pagination_class = UserPagination
    serializer_class= UserListSerializer
    lookup_field = 'public_id'

    @action(detail=False, methods=['get'])
    def list_users(self, request):
        users = CustomUser.objects.all()
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(users, request)
        serializer = UserListSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @action(detail=True, methods=['put'])
    def toggle_active(self, request, public_id=None):
        user = CustomUser.objects.get(public_id=public_id)
        user.is_active = not user.is_active
        user.save()
        return Response({'status': 'User status toggled'})

    @action(detail=True, methods=['delete'])
    def delete_user(self, request, public_id=None):
        user = CustomUser.objects.get(public_id=public_id)
        user.delete()
        return Response({'status': 'User deleted'})


# class HistoricalDataView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def get(self, request):
#         user = request.query_params.get('user')
#         start_time = request.query_params.get('start_time')
#         end_time = request.query_params.get('end_time')
#
#         if not user:
#             return Response({"error": "User is required"}, status=400)
#
#         try:
#             start_time = parse_datetime(start_time) if start_time else None
#             end_time = parse_datetime(end_time) if end_time else None
#
#             if not start_time:
#                 start_time = datetime.min
#
#             if not end_time:
#                 end_time = datetime.now()
#
#             parameters = ['PH', 'temperature', 'tds', 'do', 'humidity']
#             historical_data = {}
#
#             for param in parameters:
#                 data = SensorData.objects.filter(
#                     user__username=user,
#                     timestamp__range=(start_time, end_time)
#                 ).values('timestamp', param).order_by('timestamp')
#
#                 historical_data[param] = [
#                     {
#                         "timestamp": entry['timestamp'].isoformat(),
#                         param: float(entry[param]) if entry[param] is not None else None
#                     } for entry in data
#                 ]
#
#             return Response(historical_data)
#         except Exception as e:
#             return Response({"error": str(e)}, status=500)

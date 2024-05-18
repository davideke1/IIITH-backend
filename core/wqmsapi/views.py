from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.shortcuts import render
from django.utils.dateparse import parse_datetime, parse_date
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework import viewsets

from core.wqmsapi.permissions import IsAdminOrReadOnly
from core.wqmsapi.serializers import ActivityLogSerializer, PublishedNotificationsSerializer, \
    SensorDataSerializer, UserLocationSerializer, UserSerializer, SensorDataExportSerializer, UserFeedbackSerializer
from core.wqmsapi.models import ActivityLog, CustomUser, Feedback, Notification, SensorData
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
import csv
from django.http import HttpResponse
import pandas as pd


@api_view(['GET'])
def hello_world(request):
    return Response({'message': 'Hello, world i hate rajiv!'})

@login_required
def check_authentication(request):
    return JsonResponse({'authenticated': request.user.is_authenticated, 'is_staff': request.user.is_staff, 'user': request.user.username})

class UserViewSet(viewsets.ModelViewSet):
    http_method_names = {'patch', 'get'}
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return CustomUser.objects.all()
        return CustomUser.objects.exclude(is_superuser=True)

    def get_object(self):
        try:
            obj = CustomUser.objects.get_object_by_public_id(self.kwargs['pk'])
            self.check_object_permissions(self.request, obj)
            return obj
        except CustomUser.DoesNotExist:
            raise Http404

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        # Validate the serializer
        serializer.is_valid(raise_exception=True)

        # Ensure email and username are unique
        email = serializer.validated_data.get('email')
        username = serializer.validated_data.get('username')
        # print(email,username)
        if CustomUser.objects.exclude(pk=instance.pk, email=instance.email).filter(email=email).exists():
            return Response({'error': 'Email already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        if CustomUser.objects.exclude(pk=instance.pk, username=instance.username).filter(username=username).exists():
            return Response({'error': 'Username already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        # Save the serializer
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserLocationViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminUser]

    def list(self, request):
        users = CustomUser.objects.filter(latitude__isnull=False, longitude__isnull=False)
        serializer = UserLocationSerializer(users, many=True)
        return Response(serializer.data)


class PublishedNotificationsPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def paginate_queryset(self, queryset, request, view=None):
        page_number = request.query_params.get(self.page_query_param, 1)
        try:
            return super().paginate_queryset(queryset, request, view)
        except ValueError:
            # If the requested page is not available, return page 1 instead
            self.page.number = 1
            return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        response = super().get_paginated_response(data)
        response.data['page_number'] = self.page.number
        return response


class PublishedNotificationsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Notification.objects.filter(status=Notification.PUBLISHED).order_by('-created_at')
    serializer_class = PublishedNotificationsSerializer
    pagination_class = PublishedNotificationsPagination
    permission_classes = [IsAuthenticated]


class ActivityLogViewSet(viewsets.ModelViewSet):
    queryset = ActivityLog.objects.all()
    serializer_class = ActivityLogSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user__email', 'action']


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        user = CustomUser.objects.get_object_by_public_id(pk)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)



class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = UserFeedbackSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        if request.user.is_staff:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            return Response({"error": "You don't have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)



class UserSensorDataViewSet(viewsets.ModelViewSet):
    queryset = SensorData.objects.all()
    serializer_class = SensorDataSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def user_historical_data(self, request):
        user_id = request.query_params.get('user_id')
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')

        if not user_id:
            return Response({'error': 'user_id query parameter is required'}, status=400)

        try:
            user = CustomUser.objects.get(public_id=user_id)
            user_sensor_data = SensorData.objects.filter(user=user).order_by('timestamp')

            if start_date_str:
                start_date = parse_date(start_date_str)
                if end_date_str:
                    end_date = parse_date(end_date_str)
                else:
                    end_date = datetime.now()
            else:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=3)

            user_sensor_data = user_sensor_data.filter(timestamp__range=[start_date, end_date])

            serializer = SensorDataSerializer(user_sensor_data, many=True)
            return Response(serializer.data)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)
        except SensorData.DoesNotExist:
            return Response({'error': 'No data found for the specified user'}, status=404)

    @action(detail=False, methods=['get'])
    def export_sensor_data(self, request):
        user_id = request.query_params.get('publicId')
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')

        if not user_id:
            return Response({'error': 'user_id query parameter is required'}, status=400)

        users = CustomUser.objects.filter(public_id=user_id)
        if not users.exists():
            return Response({'error': 'User not found'}, status=404)
        user = users.first()

        user_sensor_data = SensorData.objects.filter(user=user).order_by('timestamp')

        if start_date_str and end_date_str:
            start_date = parse_datetime(start_date_str + 'T00:00:00Z')  # Assuming the format is YYYY-MM-DD
            end_date = parse_datetime(end_date_str + 'T23:59:59Z')
            user_sensor_data = user_sensor_data.filter(timestamp__range=[start_date, end_date])

        filename = "sensor_data"
        if start_date_str:
            filename += f"_from_{start_date_str}"
        if end_date_str:
            filename += f"_to_{end_date_str}"
        filename += ".csv"
        serializer = SensorDataExportSerializer(user_sensor_data, many=True)
        df = pd.DataFrame(serializer.data)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        df.to_csv(path_or_buf=response, index=False)
        return response
import csv

from django.contrib import admin

# Register your models here
from django.contrib.auth.hashers import make_password
from django.utils.timezone import is_aware
from openpyxl import Workbook
from django.http import HttpResponse
from pytz import timezone as pytz_timezone
from django.contrib import admin
from .models import CustomUser, SensorData, Notification, ActivityLog, Feedback
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from datetime import datetime


class SensorDataAdmin(admin.ModelAdmin):
    list_display = ('user', 'temperature', 'humidity', 'PH', 'tds', 'do', 'local_timestamp')
    search_fields = ('user__username', 'temperature', 'humidity', 'PH', 'tds', 'do', 'timestamp')
    list_filter = ('user', 'timestamp')
    date_hierarchy = 'timestamp'
    actions = ['export_to_csv', 'export_to_excel']

    def local_timestamp(self, obj):
        return obj.timestamp.astimezone(pytz_timezone('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S")

    local_timestamp.short_description = _('Timestamp (Asia/Kolkata)')

    def save_model(self, request, obj, form, change):
        if not change:  # Check if it's a new object being created
            obj.timestamp = timezone.now()  # Use timezone.now()
        obj.save()

    def export_to_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="sensor_data.csv"'
        writer = csv.writer(response)
        writer.writerow(['User', 'Temperature', 'Humidity', 'PH', 'TDS', 'DO', 'Timestamp'])
        for obj in queryset:
            writer.writerow([obj.user.username, obj.temperature, obj.humidity, obj.PH, obj.tds, obj.do, obj.timestamp])
        return response

    export_to_csv.short_description = _('Export to CSV')

    def export_to_excel(self, request, queryset):
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="sensor_data.xlsx"'

        workbook = Workbook()
        worksheet = workbook.active

        # Add headers
        headers = ['User', 'Temperature', 'Humidity', 'PH', 'TDS', 'DO', 'Timestamp']
        worksheet.append(headers)

        # Add data rows
        for obj in queryset:
            row = [obj.user.username, obj.temperature, obj.humidity, obj.PH, obj.tds, obj.do]

            # Convert timezone-aware datetime objects to timezone-naive datetime objects
            if is_aware(obj.timestamp):
                obj.timestamp = obj.timestamp.replace(tzinfo=None)

            row.append(obj.timestamp)  # Append the datetime object
            worksheet.append(row)

        workbook.save(response)
        return response

    export_to_excel.short_description = _('Export to Excel')


admin.site.register(SensorData, SensorDataAdmin)

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['email', 'username', 'first_name', 'last_name', 'role']
    list_filter = ['role','is_active']
    search_fields = ['email', 'username']
    ordering = ['email']
    fields = ['email', 'username', 'first_name', 'last_name','phone_no','password','thinkspeak_api_key','latitude','longitude', 'role', 'is_active','is_staff','is_superuser']

    def save_model(self, request, obj, form, change):
        # Handle password hashing for creation or update
        if not change:
            # User being created
            password = form.cleaned_data.get('password')
            if password:
                obj.password = make_password(password)
        else:
            # User being updated
            password = form.cleaned_data.get('password')
            if password:
                obj.password = make_password(password)
            else:
                # Keep existing password if not changed
                obj.password = obj.password

        # Handle role change restriction for non-superusers
        if change and 'role' in form.changed_data and not request.user.is_superuser:
            form.instance.role = 'user'

        super().save_model(request, obj, form, change)


admin.site.register(CustomUser,CustomUserAdmin)


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'subtitle', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'subtitle')
    actions = ['publish_notifications']

    def publish_notifications(self, request, queryset):
        queryset.update(status=Notification.PUBLISHED)

    publish_notifications.short_description = "Publish selected notifications"

admin.site.register(Notification, NotificationAdmin)

class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp')
    search_fields = ('user__email', 'action')
    list_filter = ('timestamp',)

admin.site.register(ActivityLog, ActivityLogAdmin)

admin.site.register(Feedback)
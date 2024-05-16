from django.contrib import admin
from .models import CustomUser
# Register your models here.
from django.contrib import admin
from .models import CustomUser, SensorData
from django.utils import timezone
from datetime import datetime

class SensorDataAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if not change:  # Check if it's a new object being created
            obj.timestamp = datetime.now(timezone.utc)
        obj.save()

admin.site.register(SensorData, SensorDataAdmin)
class CustomUserAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if not change:  # Only set password if creating a new user
            obj.set_password(obj.password)
        obj.save()

admin.site.register(CustomUser,CustomUserAdmin)

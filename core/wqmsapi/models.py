import uuid
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.http import Http404
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from phonenumber_field.modelfields import PhoneNumberField
import logging

# logger = logging.getLogger(__name__)
class UserManager(BaseUserManager):
    def get_object_by_public_id(self,public_id):
        try:
            instance = self.get(public_id=public_id)
            return instance
        except(ObjectDoesNotExist, ValueError,TypeError):
            return Http404
        
    def create_user(self,username,email,password=None, **kwargs):
        """Create and return a `User` with an email, phone
            number, username and password."""
        

        if username is None:
            raise TypeError("User must have a username.")
        if email is None:
            raise TypeError("User must have a email.")
        if password is None:
            raise TypeError("User must have a password.")
        user = self.model(username=username, email=self.normalize_email(email), **kwargs)
        user.set_password(password)
        user.save(using=self._db)

        return user
    def create_superuser(self,username,email,password,**kwargs):
        """
 Create and return a `User` with superuser (admin)
 permissions.
 """
        
        if username is None:
            raise TypeError("Superuser must have a username.")
        if email is None:
            raise TypeError("Superuser must have a email.")
        if password is None:
            raise TypeError("Superuser must have a password.")
        
        user = self.create_user(username,email,password,**kwargs)
        user.is_active= True
        user.is_superuser= True
        user.is_staff = True
        user.save(using=self._db)

        return user
        

class CustomUser(AbstractBaseUser,PermissionsMixin):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'),
    )

    public_id = models.UUIDField(db_index=True, unique=True,
                                 default=uuid.uuid4, editable=False)
    username = models.CharField(db_index=True, max_length=255,unique=True)
    first_name= models.CharField(max_length=255)
    last_name= models.CharField(max_length=255)
    email = models.EmailField(db_index=True, unique=True)
    phone_no =PhoneNumberField(max_length=10,blank=True, unique=True, null=True)
    # location= models.PointField(blank=True,null=True)
    longitude = models.FloatField(null=True, default=None)
    latitude = models.FloatField(null=True, default=None)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    thinkspeak_api_key = models.CharField(max_length=255, blank=True,null=True, default=None)
    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


    objects = UserManager()

    def __str__(self):
        return f"{self.email}"
    
    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"
    
    
class SensorData(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    temperature = models.DecimalField(max_digits=10, decimal_places=2)
    humidity = models.DecimalField(max_digits=10, decimal_places=2)
    PH = models.DecimalField(max_digits=10, decimal_places=2)
    tds = models.DecimalField(max_digits=10, decimal_places=2)
    do = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.timestamp}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        channel_layer = get_channel_layer()
        
        if channel_layer:  # Only send if not already pushed
            user_public_id = self.user.public_id.hex
            async_to_sync(channel_layer.group_send)(
                f'sensor_data_{user_public_id}',
                {
                    'type': 'send_sensor_data',
                    'data': {
                        'temperature': str(self.temperature),
                        'humidity': str(self.humidity),
                        'PH': str(self.PH),
                        'tds': str(self.tds),
                        'do': str(self.do),
                        'timestamp': self.timestamp.isoformat(),
                    }
                }
            )


class Notification(models.Model):
    DRAFT = 'draft'
    PUBLISHED = 'published'
    STATUS_CHOICES = [
        (DRAFT, 'Draft'),
        (PUBLISHED, 'Published'),
    ]

    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=DRAFT)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.title} - {self.subtitle}"

    def publish(self):
        self.status = self.PUBLISHED
        self.save()


class ActivityLog(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.action} - {self.timestamp}"
    
class Feedback(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
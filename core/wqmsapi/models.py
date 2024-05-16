import uuid
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.http import Http404

from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField

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
        user.is_superuser= True
        user.is_staff = True
        user.save(using=self._db)

        return user
        

class CustomUser(AbstractBaseUser,PermissionsMixin):
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
    thinkspeak_api_key = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
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
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    temperature = models.DecimalField(max_digits=10, decimal_places=2)
    humidity = models.DecimalField(max_digits=10, decimal_places=2)
    PH = models.DecimalField(max_digits=10, decimal_places=2)
    tds = models.DecimalField(max_digits=10, decimal_places=2)
    do = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.timestamp}"
    # def save(self, *args, **kwargs):
    #     if not self.user.public_id:
    #         self.timestamp = datetime.now(timezone.utc)
    #         self.timestamp = self.timestamp.replace(microsecond=0)
    #     return super(SensorData, self).save(*args, **kwargs)
    
class Notifications(models.Model):
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.title} - {self.subtitle}"
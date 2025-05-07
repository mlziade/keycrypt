import uuid
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now

def get_expiration_time():
    return now() + timedelta(hours=1)

class Profile(AbstractUser):
    ## AbstractUser Fields that are inhereted ## 
    # username = models.CharField(max_length=150, unique=True)
    # first_name = models.CharField(max_length=150, blank=True)
    # last_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=False, unique=True)
    # password = models.CharField(max_length=128)
    # is_staff = models.BooleanField(default=False)
    # is_active = models.BooleanField(default=True)
    # is_superuser = models.BooleanField(default=False)
    # last_login = models.DateTimeField(null=True, blank=True)
    # date_joined = models.DateTimeField(default=timezone.now)

    ## Custom Fields ##
    # profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    personal_url = models.URLField(blank=True, null=True)

    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

class ResetPasswordLink(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=get_expiration_time)

    def __str__(self):
        return f"Reset link for {self.user.username}"
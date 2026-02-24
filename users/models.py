from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    full_name = models.CharField(max_length=200, blank=True, default="")
    phone_number = models.CharField(max_length=20, blank=True, default="")
    job_title = models.CharField(max_length=100, blank=True, default="")
    referral_code = models.CharField(max_length=50, unique=True, db_index=True)
    referred_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='referrals')
    credit_points = models.PositiveIntegerField(default=0)
    def __str__(self):
        return self.user.email

from django.conf import settings
from django.db import models


class Client(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="clients"
    )
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, default="")
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

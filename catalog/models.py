from django.conf import settings
from django.db import models


class Product(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="products"
    )
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True, default="")

    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

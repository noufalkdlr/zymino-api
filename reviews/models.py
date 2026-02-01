from django.db import models
from django.conf import settings


class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Client(models.Model):
    phone_number = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.phone_number


class Review(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
        null=True,
    )
    tags = models.ManyToManyField(Tag, related_name="reviews")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="reviews")

    def __str__(self):
        return self.client.phone_number

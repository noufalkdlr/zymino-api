from django.db import models
from django.conf import settings


class Client(models.Model):
    phone_number = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.phone_number


class Tag(models.Model):
    class TagCategory(models.TextChoices):
        POSITIVE = "POSITIVE", "Positive"
        NEGATIVE = "NEGATIVE", "Negative"

    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=20, choices=TagCategory.choices)

    def __str__(self):
        return self.name


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

import uuid
import phonenumbers
from django.db import models
from django.conf import settings
from .utils import hash_phone_number


class Client(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=100, unique=True)

    def save(self, *args, **kwargs):
        if not self.phone_number.startswith("sha256$"):
            try:
                self.phone_number = hash_phone_number(self.phone_number)
            except phonenumbers.NumberParseException:
                raise ValueError("Invalid phone number format")

            except ValueError as ve:
                raise ve

            except Exception as e:
                raise ValueError(f"Error processing number: {e}")

        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.id)


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
        return str(self.client.id)

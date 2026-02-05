import uuid
import phonenumbers
import hashlib
from django.db import models
from django.conf import settings


class Client(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=100, unique=True)

    def save(self, *args, **kwargs):
        if self.phone_number.startswith("sha256$"):
            super().save(*args, **kwargs)
            return

        try:
            parsed_number = phonenumbers.parse(self.phone_number, None)
            if phonenumbers.is_valid_number(parsed_number):
                clean_number = phonenumbers.format_number(
                    parsed_number, phonenumbers.PhoneNumberFormat.E164
                )
                hashed_value = hashlib.sha256(clean_number.encode()).hexdigest()
                self.phone_number = f"sha256${hashed_value}"
        except Exception as e:
            raise ValueError(f"Invalid phone number format: {e}")
        super().save(*args, **kwargs)

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

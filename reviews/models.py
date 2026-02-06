import uuid
import phonenumbers
import hashlib
from django.db import models
from django.conf import settings


class Client(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=100, unique=True)

    def save(self, *args, **kwargs):
        if not self.phone_number.startswith("sha256$"):
            try:
                parsed_number = phonenumbers.parse(self.phone_number, "IN")
                if not phonenumbers.is_valid_number(parsed_number):
                    raise ValueError("Phone number is not valid")

                clean_number = phonenumbers.format_number(
                    parsed_number, phonenumbers.PhoneNumberFormat.E164
                )

                if not hasattr(settings, "PHONE_HASH_SALT"):
                    raise ValueError("PHONE_HASH_SALT not found in settings!")

                salted_number = clean_number + settings.PHONE_HASH_SALT

                hashed_value = hashlib.sha256(salted_number.encode()).hexdigest()
                self.phone_number = f"sha256${hashed_value}"

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
        return self.client.phone_number

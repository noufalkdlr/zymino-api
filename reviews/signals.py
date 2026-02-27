from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import F
from .models import Review


@receiver(post_save, sender=Review)
def add_credit_on_review(sender, instance, created, **kwargs):

    if created:
        if hasattr(instance.author, "profile"):
            user_profile = instance.author.profile
            user_profile.credit_points = F("credit_points") + 3
            user_profile.save(update_fields=["credit_points"])

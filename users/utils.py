import random
import string
from django.conf import settings
from django.core.mail import send_mail


def generate_unique_referral_code():
    from .models import UserProfile

    while True:
        code = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if not UserProfile.objects.filter(referral_code=code).exists():
            return code


def generate_otp(length=6):
    return "".join(random.choices(string.digits, k=length))


def send_otp_email(email, otp):
    subject = "Your Cashevide Verification Code"
    message = f"Welcome to Cashevide!\n\nYour verification code for signup is: {otp}\n\nThis code will expire in 5 minutes.\n\nThank you!"
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]

    send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=recipient_list,
        fail_silently=False,
    )

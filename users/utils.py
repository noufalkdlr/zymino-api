import random
import string

from .models import UserProfile


def generate_unique_referral_code(username):
    while True:
        suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        code = f"{username.upper()}{suffix}"
        if not UserProfile.objects.filter(referral_code=code).exists():
            return code

import random
import string

def generate_unique_referral_code():
    from .models import UserProfile
    while True:
        code = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if not UserProfile.objects.filter(referral_code=code).exists():
            return code

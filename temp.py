import secrets
import string
import random

# കൂടുതൽ സുരക്ഷിതമായ രീതി:
suffix = "".join(
    random.choice(string.ascii_uppercase + string.digits) for _ in range(6)
)

print(suffix)

import hashlib
import phonenumbers
from django.conf import settings


def hash_phone_number(phone_number):
    try:
        parsed_number = phonenumbers.parse(phone_number, "IN")
        if not phonenumbers.is_valid_number(parsed_number):
            raise ValueError("Phone number is not valid")

        clean_number = phonenumbers.format_number(
            parsed_number, phonenumbers.PhoneNumberFormat.E164
        )

        if not hasattr(settings, "PHONE_HASH_SALT"):
            raise ValueError("PHONE_HASH_SALT not found in settings!")

        salted_number = clean_number + settings.PHONE_HASH_SALT

        hashed_value = hashlib.sha256(salted_number.encode()).hexdigest()
        phone_number = f"sha256${hashed_value}"

        return phone_number

    except phonenumbers.NumberParseException:
        raise ValueError("Invalid phone number format")

    except ValueError as ve:
        raise ve

    except Exception as e:
        raise ValueError(f"Error processing number: {e}")

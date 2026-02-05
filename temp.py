import hashlib
import phonenumbers


# name = input("Enter name:")
#
# hashed_name = hashlib.sha256(name.encode()).hexdigest()
# hashed_name = f"sha256${hashed_name}"
#
# print(hashed_name)


number = "+91974646931-93"

parsed_number = phonenumbers.parse(number, None)
print(parsed_number)

if phonenumbers.is_valid_number(parsed_number):
    print(parsed_number)
    clean_number = phonenumbers.format_number(
        parsed_number, phonenumbers.PhoneNumberFormat.E164
    )
    print(clean_number)
    hashed_value = hashlib.sha256(clean_number.encode()).hexdigest()
    hashed_value = f"sha256${hashed_value}"
    print(hashed_value)
else:
    print(f"{number} is not valid")

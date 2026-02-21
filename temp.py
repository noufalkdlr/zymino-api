from typing import Any

attrs: dict[str, Any] = {
    "email": "noufal@zymino.com",
    "password": "mypassword123",
    "platform": "mobile",
}
user = {
    "id": 1,
    "email": "noufal@zymino.com",
    "password": "mypassword123",
    "isActive": True,
}
attrs["user"] = user

print(attrs)

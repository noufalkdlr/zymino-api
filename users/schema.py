from rest_framework import serializers
from drf_spectacular.utils import extend_schema, extend_schema_view, inline_serializer
from .serializers import UserSignUpSerializer, UserLoginSerializer, UserSerializer


USER_SIGNUP_SCHEMA = extend_schema_view(
    post=extend_schema(
        tags=["Authentication"],
        summary="User Registration / Sign Up",
        description="Registers a new user in the system.",
        responses={
            201: inline_serializer(
                name="SignupResponse",
                fields={
                    "message": serializers.CharField(
                        default="User registered successfully!"
                    ),
                    "data": UserSignUpSerializer(),
                },
            )
        },
    )
)

USER_LOGIN_SCHEMA = extend_schema_view(
    post=extend_schema(
        tags=["Authentication"],
        summary="User Login (Multi-platform)",
        description="Authenticates the user using their credentials. \n\n"
        "**Token Delivery:**\n"
        "* If platform is `web`: JWT tokens are set securely as HttpOnly cookies.\n"
        "* If platform is `mobile` (default): JWT tokens are returned directly in the JSON response.",
        request=UserLoginSerializer,
    )
)

USER_LOGOUT_SCHEMA = extend_schema_view(
    post=extend_schema(
        tags=["Authentication"],
        summary="User Logout",
        description="Logs out the user by blacklisting their refresh token. If platform is `web`, the token is automatically taken from the cookies.",
        request=inline_serializer(
            name="LogoutRequest",
            fields={
                "refresh": serializers.CharField(
                    required=False,
                    help_text="Provide refresh token for mobile platform",
                )
            },
        ),
        responses={200: dict},
    )
)

TOKEN_REFRESH_SCHEMA = extend_schema_view(
    post=extend_schema(
        tags=["Authentication"],
        summary="Refresh Access Token",
        description="Generates a new access token using a valid refresh token. Platform defaults to `mobile`.",
        request=inline_serializer(
            name="TokenRefreshRequest",
            fields={
                "refresh": serializers.CharField(required=False),
                "platform": serializers.ChoiceField(
                    choices=["web", "mobile"], required=False, default="mobile"
                ),
            },
        ),
    )
)

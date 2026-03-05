from rest_framework import serializers
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    inline_serializer,
    OpenApiParameter,
    OpenApiResponse,
)
from drf_spectacular.types import OpenApiTypes
from .serializers import (
    UserDetailSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
)


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
                    "data": UserDetailSerializer(),
                },
            )
        },
    )
)

USER_DELETE_SCHEMA = extend_schema_view(
    delete=extend_schema(
        tags=["Authentication"],
        summary="Delete User Account",
        description="Permanently deletes the currently authenticated user's account and their profile. If the request is from a web platform, it also clears the authentication cookies.",
    )
)

USER_PROFILE_SCHEMA = extend_schema_view(
    get=extend_schema(
        tags=["Users"],
        summary="Get User Profile",
        description="Retrieves the profile information of the currently authenticated user.",
    ),
    patch=extend_schema(
        tags=["Users"],
        summary="Partial Update User Profile",
        description="Updates specific fields of the user's profile.",
        request={"multipart/form-data": UserProfileSerializer},
    ),
    put=extend_schema(
        tags=["Users"],
        summary="Update User Profile",
        description="Updates the entire profile of the user.",
        request={"multipart/form-data": UserProfileSerializer},
    ),
)

USER_CHECK_FIELD_SCHEMA = extend_schema_view(
    get=extend_schema(
        tags=["Users"],
        summary="Check Field Availability",
        description="Checks whether a specific field (like 'username' or 'email') is already taken in the database. \n\n"
        "Returns `is_available: true` if the value is not taken and can be used. "
        "Returns an error if the field is invalid or missing.",
        parameters=[
            OpenApiParameter(
                name="field",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="The name of the field to check. Allowed values: `username`, `email`.",
                required=True,
            ),
            OpenApiParameter(
                name="value",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="The value you want to check for availability.",
                required=True,
            ),
        ],
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

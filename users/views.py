from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.utils import extend_schema, extend_schema_view, inline_serializer
from .serializers import UserSignUpSerializer, UserLoginSerializer, UserSerializer


@extend_schema_view(
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
class UserSignupView(CreateAPIView):
    serializer_class = UserSignUpSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response(
            {
                "message": "User registered successfully!",
                "data": response.data,
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema_view(
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
class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)

        if serializer.is_valid():
            validated_data = serializer.validated_data

            user = validated_data.get("user")
            platform = validated_data.get("platform", "mobile")

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            if platform == "web":
                response = Response(
                    {
                        "message": "login successful",
                        "user": UserSerializer(user).data,
                    },
                    status=status.HTTP_200_OK,
                )
                response.set_cookie(
                    key="access_token",
                    value=access_token,
                    httponly=True,
                    secure=True,
                    samesite="Strict",
                )
                response.set_cookie(
                    key="refresh_token",
                    value=str(refresh),
                    httponly=True,
                    secure=True,
                    samesite="Strict",
                )
            else:
                response = Response(
                    {
                        "message": "login successful",
                        "user": UserSerializer(user).data,
                        "access": access_token,
                        "refresh": str(refresh),
                    },
                    status=status.HTTP_200_OK,
                )
            return response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
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
class LogoutView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(
                {"error": "Refresh token is required to logout"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

            response = Response(
                {"message": "Successfully logged out"}, status=status.HTTP_200_OK
            )
            response.delete_cookie("access_token")
            response.delete_cookie("refresh_token")
            return response

        except Exception:
            return Response(
                {"error": "Invalid or expired token"},
                status=status.HTTP_400_BAD_REQUEST,
            )


@extend_schema_view(
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
class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh")
        platform = request.data.get("platform")

        if not refresh_token:
            refresh_token = request.COOKIES.get("refresh_token")
            if refresh_token and not platform:
                platform = "web"

        if not platform:
            platform = "mobile"

        if not refresh_token:
            return Response(
                {"error": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = {"refresh": refresh_token}
        serializer = self.get_serializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            return Response(
                {"error": "Invalid or expired refresh token"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        validated_data = serializer.validated_data
        access_token = validated_data.get("access")
        new_refresh_token = validated_data.get("refresh", refresh_token)
        if platform == "web":
            response = Response(
                {"message": "Token refreshed successfully"}, status=status.HTTP_200_OK
            )

            response.set_cookie(
                "access_token",
                access_token,
                httponly=True,
                secure=True,
                samesite="Strict",
            )
            response.set_cookie(
                "refresh_token",
                new_refresh_token,
                httponly=True,
                secure=True,
                samesite="Strict",
            )
        else:
            response = Response(
                {
                    "message": "Token refreshed successfully",
                    "access": access_token,
                    "refresh": new_refresh_token,
                },
                status=status.HTTP_200_OK,
            )
        return response

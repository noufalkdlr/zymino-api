from django.conf import settings
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView, DestroyAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
import logging
from .models import UserProfile, User
from .serializers import (
    UserDetailSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
)
from .schema import (
    USER_LOGIN_SCHEMA,
    USER_PROFILE_SCHEMA,
    USER_CHECK_FIELD_SCHEMA,
    USER_LOGOUT_SCHEMA,
    USER_SIGNUP_SCHEMA,
    TOKEN_REFRESH_SCHEMA,
    USER_DELETE_SCHEMA,
)

logger = logging.getLogger(__name__)


@USER_SIGNUP_SCHEMA
class UserSignupView(CreateAPIView):
    serializer_class = UserDetailSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            platform = request.data.get("platform", "mobile")

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            if platform == "web":
                response = Response(
                    {
                        "message": "login successful",
                        "user": UserDetailSerializer(user).data,
                    },
                    status=status.HTTP_201_CREATED,
                )
                response.set_cookie(
                    key="access_token",
                    value=access_token,
                    httponly=True,
                    secure=not settings.DEBUG,
                    samesite="Lax",
                    domain=settings.COOKIE_DOMAIN,
                )
                response.set_cookie(
                    key="refresh_token",
                    value=str(refresh),
                    httponly=True,
                    secure=not settings.DEBUG,
                    samesite="Lax",
                    domain=settings.COOKIE_DOMAIN,
                )
            else:
                response = Response(
                    {
                        "message": "login successful",
                        "user": UserDetailSerializer(user).data,
                        "access": access_token,
                        "refresh": str(refresh),
                    },
                    status=status.HTTP_201_CREATED,
                )
            return response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@USER_DELETE_SCHEMA
class UserDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user = request.user
        user.delete()

        response = Response(
            {"message": "Account successfully deleted."},
            status=status.HTTP_204_NO_CONTENT,
        )

        return response


@USER_PROFILE_SCHEMA
class UserProfileView(RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


@USER_CHECK_FIELD_SCHEMA
class CheckFieldExistsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        field = request.query_params.get("field")
        value = request.query_params.get("value")

        if not field or not value:
            return Response(
                {"error": "Please provide both 'field' and 'value'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        allowed_fields = ["username", "email"]

        if field not in allowed_fields:
            return Response(
                {"error": f"Checking '{field}' is not allowed or invalid."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        filter_kwargs = {field: value}

        try:
            is_taken = User.objects.filter(**filter_kwargs).exists()
            return Response({"is_available": not is_taken})

        except Exception as e:
            logger.error(f"Error checking field {field}: {e}")
            return Response(
                {"error": "An unexpected error occurred. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@USER_LOGIN_SCHEMA
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
                        "user": UserDetailSerializer(user).data,
                    },
                    status=status.HTTP_200_OK,
                )
                response.set_cookie(
                    key="access_token",
                    value=access_token,
                    httponly=True,
                    secure=not settings.DEBUG,
                    samesite="Lax",
                    domain=settings.COOKIE_DOMAIN,
                )
                response.set_cookie(
                    key="refresh_token",
                    value=str(refresh),
                    httponly=True,
                    secure=not settings.DEBUG,
                    samesite="Lax",
                    domain=settings.COOKIE_DOMAIN,
                )
            else:
                response = Response(
                    {
                        "message": "login successful",
                        "user": UserDetailSerializer(user).data,
                        "access": access_token,
                        "refresh": str(refresh),
                    },
                    status=status.HTTP_200_OK,
                )
            return response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@USER_LOGOUT_SCHEMA
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
            response.delete_cookie("access_token", domain=settings.COOKIE_DOMAIN)
            response.delete_cookie("refresh_token", domain=settings.COOKIE_DOMAIN)
            return response

        except Exception:
            return Response(
                {"error": "Invalid or expired token"},
                status=status.HTTP_400_BAD_REQUEST,
            )


@TOKEN_REFRESH_SCHEMA
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
                secure=not settings.DEBUG,
                samesite="Lax",
                domain=settings.COOKIE_DOMAIN,
            )
            response.set_cookie(
                "refresh_token",
                new_refresh_token,
                httponly=True,
                secure=not settings.DEBUG,
                samesite="Lax",
                domain=settings.COOKIE_DOMAIN,
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

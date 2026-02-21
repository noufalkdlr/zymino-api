from django.conf import settings
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from .serializers import (
    UserDetailSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
)
from .schema import (
    USER_LOGIN_SCHEMA,
    USER_PROFILE_SCHEMA,
    USER_LOGOUT_SCHEMA,
    USER_SIGNUP_SCHEMA,
    TOKEN_REFRESH_SCHEMA,
)


@USER_SIGNUP_SCHEMA
class UserSignupView(CreateAPIView):
    serializer_class = UserDetailSerializer
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


@USER_PROFILE_SCHEMA
class UserProfileView(RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile  # type: ignore


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

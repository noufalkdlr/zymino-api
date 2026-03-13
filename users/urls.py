from django.urls import path
from .views import (
    SignupOTPRequestView,
    PasswordResetOTPRequestView,
    SignupOTPVerificationView,
    UserSignupView,
    LoginView,
    LogoutView,
    CustomTokenRefreshView,
    UserProfileView,
    CheckFieldExistsView,
    PasswordChangeView,
    PasswordResetView,
    PasswordResetOTPVerificationView,
    UserDeleteView,
)

urlpatterns = [
    path("signup-request-otp/", SignupOTPRequestView.as_view(), name="signup_send_otp"),
    path(
        "signup-verify-otp/",
        SignupOTPVerificationView.as_view(),
        name="signup_verify_otp",
    ),
    path("signup/", UserSignupView.as_view(), name="user_signup"),
    path("profile/me/", UserProfileView.as_view(), name="user_profile"),
    path("profile/delete/", UserDeleteView.as_view(), name="user_delete"),
    path("check-user/", CheckFieldExistsView.as_view(), name="check-user"),
    path("login/", LoginView.as_view(), name="login"),
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("change-password/", PasswordChangeView.as_view(), name="change_password"),
    path(
        "password-reset-request-otp/",
        PasswordResetOTPRequestView.as_view(),
        name="password_reset_send_otp",
    ),
    path(
        "password-reset-verify-otp/",
        PasswordResetOTPVerificationView.as_view(),
        name="password_reset_verify_otp",
    ),
    path("reset-password/", PasswordResetView.as_view(), name="reset_password"),
    path("logout/", LogoutView.as_view(), name="logout"),
]

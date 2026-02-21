from django.urls import path
from .views import (
    UserSignupView,
    LoginView,
    LogoutView,
    CustomTokenRefreshView,
    UserProfileView,
)

urlpatterns = [
    path("signup/", UserSignupView.as_view(), name="user_signup"),
    path("profile/me/", UserProfileView.as_view(), name="user_profile"),
    path("login/", LoginView.as_view(), name="login"),
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
]

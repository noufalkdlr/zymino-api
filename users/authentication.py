from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed


class MultiPlatformJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)
        if header is not None:
            raw_token = self.get_raw_token(header)
        else:
            raw_token = request.COOKIES.get("access_token")

        if not raw_token:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)  # type: ignore
        except AuthenticationFailed as e:
            raise AuthenticationFailed(f"Token validation failed: {str(e)}")

        try:
            user = self.get_user(validated_token)
            return user, validated_token
        except AuthenticationFailed as e:
            raise AuthenticationFailed(f"error retrieving user: {str(e)}")

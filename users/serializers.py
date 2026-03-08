from django.db.models import F
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, UserProfile
from .services import create_user_account
from django.core.cache import cache


class OTPRequestSerializer(serializers.Serializer):
    """Serializer for requesting an OTP"""

    email = serializers.EmailField(required=True, write_only=True)

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                "An account with this email address already exists."
            )

        return email


class OTPVerificationSerializer(serializers.Serializer):
    """Serializer for verifying the OTP"""

    otp = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(write_only=True, required=True)

    def validate(self, attrs):
        otp = attrs.get("otp")
        email = attrs.get("email")

        cached_otp = cache.get(f"otp_{email}")
        if not cached_otp:
            raise serializers.ValidationError(
                {
                    "otp": "The OTP has expired or does not exist. Please request a new one."
                }
            )
        if cached_otp != otp:
            raise serializers.ValidationError(
                {"otp": "The provided OTP is invalid. Please try again."}
            )

        cache.set(f"verified_{email}", True, timeout=900)

        return attrs


class UserDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(write_only=True, required=True)
    referral_code_input = serializers.CharField(
        write_only=True, required=True, allow_blank=False, allow_null=False
    )
    platform = serializers.ChoiceField(
        choices=["web", "mobile"], default="mobile", write_only=True, required=False
    )

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "password",
            "full_name",
            "referral_code_input",
            "platform",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def validate_referral_code_input(self, referral_code_input):
        if not UserProfile.objects.filter(referral_code=referral_code_input).exists():
            raise serializers.ValidationError(
                "The referral code provided is incorrect. Please check it."
            )

        return referral_code_input

    def validate(self, attrs):
        email = attrs.get("email")

        is_verified = cache.get(f"verified_{email}")

        if not is_verified:
            raise serializers.ValidationError(
                {
                    "email": "This email address has not been verified. Please verify it using an OTP first."
                }
            )

        return attrs

    def create(self, validated_data):
        return create_user_account(validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    user_id = serializers.IntegerField(source="user.id", read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            "user_id",
            "email",
            "username",
            "full_name",
            "profile_picture",
            "phone_number",
            "job_title",
            "referral_code",
            "referred_by",
            "credit_points",
        ]
        read_only_fields = [
            "referral_code",
            "referred_by",
            "credit_points",
        ]


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True)
    platform = serializers.ChoiceField(
        choices=["web", "mobile"], default="mobile", required=False
    )

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(email=email, password=password)
        if user and user.is_active:
            attrs["user"] = user
            return attrs
        raise serializers.ValidationError("Incorrect credentials!")

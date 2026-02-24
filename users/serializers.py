from django.db import transaction
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, UserProfile
from .utils import generate_unique_referral_code


class UserDetailSerializer(serializers.ModelSerializer):
    referral_code_input = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ["id", "email", "username", "password", "referral_code_input"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate_referral_code_input(self, referral_code_input):
        if referral_code_input:
            if not UserProfile.objects.filter(
                referral_code=referral_code_input
            ).exists():
                raise serializers.ValidationError(
                    "The referral code provided is incorrect. Please check it."
                )
        return referral_code_input

    def create(self, validated_data):
        referral_code_input = validated_data.pop("referral_code_input", None)
        with transaction.atomic():
            user = User.objects.create_user(**validated_data)

            referred_by_user = None
            if referral_code_input:
                referrer_profile = UserProfile.objects.get(
                    referral_code=referral_code_input
                )
                referred_by_user = referrer_profile.user

            referral_code = generate_unique_referral_code()

            UserProfile.objects.create(
                user=user, referral_code=referral_code, referred_by=referred_by_user
            )
            return user


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

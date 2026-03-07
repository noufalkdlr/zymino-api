from django.db.models import F
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, UserProfile
from .services import create_user_account


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

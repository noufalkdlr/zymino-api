from rest_framework import serializers
from users.models import User, MemberProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "username", "password"]
        extra_kwargs = {"password": {"write_only": True}}


class CustomerSignUpSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = MemberProfile
        fields = ["user", "phone_number"]

    def create(self, validated_data):
        user_data = validated_data.pop("user")
        user = User.objects.create_user(**user_data)
        profile = MemberProfile.objects.create(user=user, **validated_data)
        return profile

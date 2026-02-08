from rest_framework import serializers
from .models import Client, Tag, Review


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ["id", "phone_number"]


class ClientLookupSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=100, required=True)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "category"]


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["id", "author", "tags", "client"]
        read_only_fields = ["author", "client"]


class ReviewListSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = serializers.ReadOnlyField(source="author.username")

    class Meta:
        model = Review
        fields = ["id", "tags", "author"]


class UserReviewListSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.username")
    tags = TagSerializer(many=True)
    client = ClientSerializer()

    class Meta:
        model = Review
        fields = ["id", "author", "tags", "client"]

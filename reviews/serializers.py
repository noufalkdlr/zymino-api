from rest_framework import serializers
from .models import Client, Tag, Review


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ["id", "phone_number"]


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

    class Meta:
        model = Review
        fields = [
            "id",
            "author",
            "tags",
        ]

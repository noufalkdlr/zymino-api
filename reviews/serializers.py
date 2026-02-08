from rest_framework import serializers
from rest_framework.exceptions import ValidationError
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

    def validate(self, attrs):
        request = self.context.get("request")
        view = self.context.get("view")

        client_id = view.kwargs.get("client_id")  # type:ignore
        if request.method == "POST":  # type:ignore
            if Review.objects.filter(author=request.user, client__id=client_id):  # type:ignore
                raise ValidationError(
                    {"detail": "You have already reviewed this client!"}
                )

        return attrs


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

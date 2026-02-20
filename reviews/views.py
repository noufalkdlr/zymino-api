from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from users.permissions import IsSuperUser, IsOwner
from .models import Client, Tag, Review
from .utils import hash_phone_number
from .serializers import (
    ClientSerializer,
    TagSerializer,
    ReviewSerializer,
    ReviewListSerializer,
    ClientLookupSerializer,
    UserReviewListSerializer,
)
from .schema import (
    CLIENT_LOOKUP_SCHEMA,
    CLIENT_VIEWSET_SCHEMA,
    TAG_VIEWSET_SCHEMA,
    REVIEW_VIEWSET_SCHEMA,
    USER_REVIEW_VIEWSET_SCHEMA,
)


@TAG_VIEWSET_SCHEMA
class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def get_permissions(self):
        if self.action == "list":
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsSuperUser]

        return [permission() for permission in permission_classes]


@CLIENT_VIEWSET_SCHEMA
class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

    def get_permissions(self):
        if self.action in ["create", "retrieve"]:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsSuperUser]

        return [permission() for permission in permission_classes]


@CLIENT_LOOKUP_SCHEMA
class ClientLookupView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ClientLookupSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        phone_number = serializer.validated_data["phone_number"]

        try:
            hashed_number = hash_phone_number(phone_number)
            client = get_object_or_404(Client, phone_number=hashed_number)

            return Response(
                {"client_id": client.id, "message": "Client found successfully"},
                status=status.HTTP_200_OK,
            )

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception:
            return Response(
                {"error": "client not found"}, status=status.HTTP_404_NOT_FOUND
            )



@REVIEW_VIEWSET_SCHEMA
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ["list", "create"]:
            permission_classes = [IsAuthenticated]

        else:
            permission_classes = [IsSuperUser]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        client_id = self.kwargs["client_id"]
        return Review.objects.filter(client__id=client_id)

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return ReviewListSerializer
        return ReviewSerializer

    def perform_create(self, serializer):
        client_id = self.kwargs["client_id"]
        client = get_object_or_404(Client, id=client_id)
        return serializer.save(author=self.request.user, client=client)


@USER_REVIEW_VIEWSET_SCHEMA
class UserReviewViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwner]
    serializer_class = UserReviewListSerializer

    def get_queryset(self):
        return Review.objects.filter(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return UserReviewListSerializer
        return ReviewSerializer

    def create(self, request, *args, **kwargs):
        return Response(
            {"detail": "Use client endpoint to create reviews."},
            status=status.HTTP_400_BAD_REQUEST,
        )

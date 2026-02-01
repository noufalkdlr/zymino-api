from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from .models import Client, Tag, Review
from .serializers import ClientSerializer, TagSerializer, ReviewSerializer
from users.permissions import IsSuperUser, IsOwnerOrReadOnly


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

    def get_permissions(self):
        if self.action in ["create", "retrieve"]:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsSuperUser]

        return [permission() for permission in permission_classes]


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def get_permissions(self):
        if self.action == "list":
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsSuperUser]

        return [permission() for permission in permission_classes]


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ["list", "create"]:
            permission_classes = [IsAuthenticated]

        elif self.action in ["retrieve", "destroy", "update", "partial_update"]:
            permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

        else:
            permission_classes = [IsSuperUser]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        id = self.kwargs["client_id"]
        return Review.objects.filter(client__id=id)

    def perform_create(self, serializer):
        id = self.kwargs["client_id"]
        client = get_object_or_404(Client, id=id)
        return serializer.save(author=self.request.user, client=client)

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    inline_serializer,
    OpenApiParameter,
)
from .models import Client, Tag, Review
from .serializers import (
    ClientSerializer,
    TagSerializer,
    ReviewSerializer,
    ReviewListSerializer,
    ClientLookupSerializer,
    UserReviewListSerializer,
)
from users.permissions import IsSuperUser, IsOwner
from .utils import hash_phone_number


@extend_schema_view(
    list=extend_schema(
        tags=["Clients"],
        summary="List all clients (Superuser only)",
        description="Only accessible by superusers to see the full list of clients.",
    ),
    retrieve=extend_schema(
        tags=["Clients"],
        summary="Get client details",
        description="Fetch specific details of a client by their ID. Accessible by any authenticated user.",
    ),
    create=extend_schema(
        tags=["Clients"],
        summary="Create a new client",
        description="Allow users to add a new client (business) if it's not already in the system before they write a review.",
    ),
    update=extend_schema(
        tags=["Clients"], summary="Update client details (Superuser only)"
    ),
    partial_update=extend_schema(
        tags=["Clients"], summary="Partially update client details (Superuser only)"
    ),
    destroy=extend_schema(tags=["Clients"], summary="Delete a client (Superuser only)"),
)
class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

    def get_permissions(self):
        if self.action in ["create", "retrieve"]:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsSuperUser]

        return [permission() for permission in permission_classes]


@extend_schema(
    tags=["Clients"],
    summary="Lookup Client ID by Phone Number",
    description="Search for a client's unique ID using their phone number. This ID is required to post a review for that specific client.",
    request=ClientLookupSerializer,
    responses={
        200: inline_serializer(
            name="LookupSuccessResponse",
            fields={
                "client_id": serializers.UUIDField(),
                "message": serializers.CharField(default="Client found successfully"),
            },
        ),
        404: inline_serializer(
            name="LookupErrorResponse",
            fields={"error": serializers.CharField(default="client not found")},
        ),
    },
)
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


@extend_schema_view(
    list=extend_schema(
        tags=["Tags"],
        summary="List all available tags",
        description="Fetch all pre-defined tags that users can select while writing a review.",
    ),
    retrieve=extend_schema(tags=["Tags"], summary="Get details of a specific tag"),
    create=extend_schema(
        tags=["Tags"],
        summary="Create a new pre-defined tag",
        description="Only accessible by superusers. Use this to add tags that users will see in the frontend.",
    ),
    update=extend_schema(tags=["Tags"], summary="Update an existing tag"),
    partial_update=extend_schema(tags=["Tags"], summary="Partially update a tag"),
    destroy=extend_schema(tags=["Tags"], summary="Remove a tag from the system"),
)
class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def get_permissions(self):
        if self.action == "list":
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsSuperUser]

        return [permission() for permission in permission_classes]


@extend_schema_view(
    list=extend_schema(
        tags=["Reviews"],
        summary="Get reviews for a client",
        description="Retrieve all reviews associated with a specific client.",
        parameters=[
            OpenApiParameter("client_id", str, OpenApiParameter.PATH, description="The unique ID of the client.")
        ],
    ),
    create=extend_schema(
        tags=["Reviews"],
        summary="Post a review for a client",
        description="Submit a new review for a specific client.",
        parameters=[
            OpenApiParameter("client_id", str, OpenApiParameter.PATH, description="The unique ID of the client.")
        ],
    ),
    retrieve=extend_schema(
        tags=["Reviews"],
        summary="Get details of a specific review",
        description="Fetch full details of a specific review.",
        parameters=[
            OpenApiParameter("client_id", str, OpenApiParameter.PATH, description="ID of the client"),
            OpenApiParameter("pk", int, OpenApiParameter.PATH, description="Primary Key (ID) of the review") # 👈 'id' ന് പകരം 'pk'
        ]
    ),
    update=extend_schema(
        tags=["Reviews"],
        summary="Update a review (Superuser only)",
        description="Completely update a review's content.",
        parameters=[
            OpenApiParameter("client_id", str, OpenApiParameter.PATH, description="ID of the client"),
            OpenApiParameter("pk", int, OpenApiParameter.PATH, description="Primary Key (ID) of the review") # 👈 'pk'
        ]
    ),
    partial_update=extend_schema(
        tags=["Reviews"],
        summary="Partially update a review (Superuser only)",
        description="Update specific fields of a review.",
        parameters=[
            OpenApiParameter("client_id", str, OpenApiParameter.PATH, description="ID of the client"),
            OpenApiParameter("pk", int, OpenApiParameter.PATH, description="Primary Key (ID) of the review") # 👈 'pk'
        ]
    ),
    destroy=extend_schema(
        tags=["Reviews"],
        summary="Delete a review (Superuser only)",
        description="Permanently remove a review from the system.",
        parameters=[
            OpenApiParameter("client_id", str, OpenApiParameter.PATH, description="ID of the client"),
            OpenApiParameter("pk", int, OpenApiParameter.PATH, description="Primary Key (ID) of the review") # 👈 'pk'
        ]
    ),
)
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

@extend_schema_view(
    list=extend_schema(
        tags=["Reviews"],
        summary="List my reviews",
        description="Retrieve a list of all reviews written by the currently authenticated user."
    ),
    retrieve=extend_schema(
        tags=["Reviews"], 
        summary="Get details of my review",
        description="Fetch the full details of a specific review owned by the user.",
        parameters=[OpenApiParameter("id", int, OpenApiParameter.PATH)]
        
    ),
    update=extend_schema(
        tags=["Reviews"], 
        summary="Update my review",
        description="Completely update an existing review. Only the owner can perform this action.",
        parameters=[OpenApiParameter("id", int, OpenApiParameter.PATH)]
    ),
    partial_update=extend_schema(
        tags=["Reviews"], 
        summary="Partially update my review",
        description="Update specific fields of an existing review.",
        parameters=[OpenApiParameter("id", int, OpenApiParameter.PATH)]
    ),
    destroy=extend_schema(
        tags=["Reviews"], 
        summary="Delete my review",
        description="Remove a review permanently from the system.",
        parameters=[OpenApiParameter("id", int, OpenApiParameter.PATH)]
    ),
    create=extend_schema(exclude=True)
)
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

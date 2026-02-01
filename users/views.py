from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from .serializers import CustomerSignUpSerializer


class CustomerSignupView(CreateAPIView):
    serializer_class = CustomerSignUpSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response(
            {
                "message": "Customer registered successfully!",
                "data": response.data,
            },
            status=status.HTTP_201_CREATED,
        )

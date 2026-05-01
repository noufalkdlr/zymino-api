from django.db.models import Avg, Count
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from demo.models import Book
from demo.serializers import BookSerializer


class BookView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)

        count = books.aggregate(total=Count("id"), avg=Avg("id"))
        count_by_name = books.values("name").annotate(count=Count("id"))

        print(count)
        print(count_by_name)

        data = {
            "books": serializer.data,
            "count": count.get("total"),
            "count_by_name": list(count_by_name),
        }

        return Response(data)

    def post(self, request):
        serializer = BookSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response({"message": "Book added"}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

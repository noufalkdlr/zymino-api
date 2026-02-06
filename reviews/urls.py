from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClientViewSet, TagViewSet, ReviewViewSet

router = DefaultRouter()
router.register(r"clients", ClientViewSet)
router.register(r"tags", TagViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "client/<uuid:client_id>/reviews/",
        ReviewViewSet.as_view({"get": "list", "post": "create"}, name="client_review"),
    ),
    path(
        "client/<uuid:client_id>/reviews/<int:pk>/",
        ReviewViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            },
            name="client_detail",
        ),
    ),
]

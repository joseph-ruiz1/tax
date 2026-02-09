from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import DataSetViewSet

app_name = "tax"

router = DefaultRouter()
router.register(r"datasets", DataSetViewSet, basename="dataset")

urlpatterns = [
    path("api/", include(router.urls)),
    path("api/auth/", include("dj_rest_auth.urls")),
    path("api/auth/registration/", include("dj_rest_auth.registration.urls")),
]

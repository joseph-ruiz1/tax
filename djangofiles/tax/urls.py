from dj_rest_auth.views import LoginView, LogoutView, UserDetailsView
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AuthViewSet, DataSetViewSet

app_name = "tax"

router = DefaultRouter()
router.register(r"auth", AuthViewSet, basename="auth")
router.register(r"datasets", DataSetViewSet, basename="dataset")

urlpatterns = [
    path("api/", include(router.urls)),
    path("api/auth/", include("dj_rest_auth.urls")),
    path("api/register/", include("dj_rest_auth.registration.urls")),
]

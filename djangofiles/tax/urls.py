from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import DataSetViewSet, AuthViewSet

app_name = "tax"

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'datasets', DataSetViewSet, basename="dataset")


urlpatterns = [
    path('api/', include(router.urls)),
]
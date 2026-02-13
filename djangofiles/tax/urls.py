from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AuthViewSet, OptimizationViewSet

app_name = "tax"

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'optimizations', OptimizationViewSet, basename="optimization")


urlpatterns = [
    path('api/', include(router.urls)),
]

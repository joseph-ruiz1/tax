from django.urls import include, path
from django.contrib.auth.views import LogoutView
from rest_framework.routers import DefaultRouter

from .views import InputsCreateView, IndexView, RegisterView, DashboardView, LoginView, StartNewDataSetView, OutputView, UserViewSet, DataSetViewSet, AuthViewSet

app_name = "tax"

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'users', UserViewSet, basename='user')

router.register(r'datasets', DataSetViewSet, basename="dataset")


urlpatterns = [
    path('api/', include(router.urls)),

    path("login/", LoginView.as_view(), name='login'),
    path("logout/", LogoutView.as_view(next_page='login'), name='logout'),
    path("register/", RegisterView.as_view(), name='register'),
    path("users/dashboard", DashboardView.as_view(), name="dashboard"),
    path("datasets/start/", StartNewDataSetView.as_view(), name='start-dataset'),
    path("users/datasets/<int:dataset_pk>/inputs/", InputsCreateView.as_view(), name="inputs"),
    path("users/datasets/<int:dataset_pk>/output/", OutputView.as_view(), name="output"),
]
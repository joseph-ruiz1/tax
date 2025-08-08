from django.urls import path
from django.contrib.auth.views import LogoutView

from .views import InputsCreateView, IndexView, RegisterView, DashboardView, LoginView, StartNewDataSetView, OutputView

app_name = "tax"
urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("login/", LoginView.as_view(), name='login'),
    path("logout/", LogoutView.as_view(next_page='login'), name='logout'),
    path("register/", RegisterView.as_view(), name='register'),
    path("users/dashboard", DashboardView.as_view(), name="dashboard"),
    path("datasets/start/", StartNewDataSetView.as_view(), name='start-dataset'),
    path("users/datasets/<int:dataset_pk>/inputs/", InputsCreateView.as_view(), name="inputs"),
    path("users/datasets/<int:dataset_pk>/output/", OutputView.as_view(), name="output"),
]
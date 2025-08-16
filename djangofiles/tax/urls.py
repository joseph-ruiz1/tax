from django.urls import include, path
from django.contrib.auth.views import LogoutView

from .views import InputsCreateView, IndexView, RegisterView, DashboardView, LoginView, StartNewDataSetView, OutputView, UserList, UserDetail, DataSetList, DataSetDetail

from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns



app_name = "tax"
urlpatterns = [
    path('users/', UserList.as_view()),
    path('users/<int:pk>/', UserDetail.as_view()),
    path('view/', DataSetList.as_view(), name="dataset-list"),
    path('view/<int:pk>/', DataSetDetail.as_view(), name="dataset-detail"),

    path("login/", LoginView.as_view(), name='login'),
    path("logout/", LogoutView.as_view(next_page='login'), name='logout'),
    path("register/", RegisterView.as_view(), name='register'),
    path("users/dashboard", DashboardView.as_view(), name="dashboard"),
    path("datasets/start/", StartNewDataSetView.as_view(), name='start-dataset'),
    path("users/datasets/<int:dataset_pk>/inputs/", InputsCreateView.as_view(), name="inputs"),
    path("users/datasets/<int:dataset_pk>/output/", OutputView.as_view(), name="output"),
]

urlpatterns = format_suffix_patterns(urlpatterns)
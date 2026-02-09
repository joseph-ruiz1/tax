from django.contrib.auth import login, logout
from django.shortcuts import get_object_or_404
from django.db.models import Count
from django.views.generic import TemplateView
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import TaxDataSet
from .serializers import (
    CalculationEntrySerializer,
    CreateCalculationSerializer,
    LoginSerializer,
    OutputSerializer,
    TaxDataSetDetailSerializer,
    TaxDataSetSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)
from .utils import update_calculations


class IndexView(TemplateView):
    template_name = "tax/index.html"

class AuthViewSet(viewsets.ViewSet):
    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            # Create cookie
            login(request, serializer.validated_data)
            return Response({
                "success": True,
                "message": "Login successful",
            })
        return Response({
            "success": False,
            "errors": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def register(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            login(request, user)
            return Response({
                "success": True,
                "message": "Registration successful",
            }, status=status.HTTP_201_CREATED)
        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def logout(self, request):
        logout(request)
        return Response({
            "success": True,
            "message": "Logout successful",
        })

    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def check(self, request):
        if request.user.is_authenticated:
            return Response({
                "authenticated": True,
                "user": UserSerializer(request.user).data,
            })
        return Response({
            "authenticated": False,
        })

    @action(detail=False, methods=["get"])
    def me(self, request):
        return Response(UserSerializer(request.user).data)

class DataSetViewSet(viewsets.ModelViewSet):
    """Dataset dashboard page. Allows for viewing, editing, and deleting Creates are handled in CalculationEntryView."""

    queryset = TaxDataSet.objects.all()
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        # Only return those with 4 tax years
        return TaxDataSet.objects.annotate(tax_year_count=Count("tax_years")).filter(user=self.request.user).filter(tax_year_count=4)

    def get_serializer_class(self):
        if self.action == "list":
            return TaxDataSetSerializer
        elif self.action in {"retrieve", "delete"}:
            return TaxDataSetDetailSerializer
        elif self.action == "create_step":
            return CreateCalculationSerializer
        elif self.action == "new_entry":
            return CalculationEntrySerializer
        elif self.action == "results_get":
            return OutputSerializer
        elif self.action == "results_patch":
            return CalculationEntrySerializer

        raise NotImplementedError(f"No serializer for action: {self.action}")

    @action(detail=False, methods=["post"], url_path="create")
    def create_step(self, request):
        """
        Creates new TaxDataSet instance with 2024 as default election year.

        Returns TaxYearData instances so we can access IDs.
        """
        serializer = self.get_serializer(data={})
        if serializer.is_valid():
            dataset = serializer.save(user=request.user)

            return Response({
                "success": True,
                "dataset_id": dataset.id,
            }, status=status.HTTP_201_CREATED)

        return Response({
            "success": False,
            "message": "Dataset Creation failed",
            "errors": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["patch"], url_path="new")
    def new_entry(self, request, pk=None):
        """Save initial information submitted from data entry screen."""
        dataset = self.get_object()
        serializer = self.get_serializer(dataset, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                    "success": True,
                    "message": "Data saved successfully",
                    "dataset": serializer.data,
                })
        return Response({
            "success": False,
            "errors": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path="results")
    def results_get(self, request, pk=None):
        """Fetch caulcation inputs and results."""
        dataset = self.get_object()
        results = update_calculations(dataset)
        serializer = self.get_serializer(dataset,
                                         context={"results": results["optimization"],
                                                  "bracket_thresholds": results["bracket_thresholds"]})
        return Response({
            "success": True,
            "message": "Get Successful",
            "form": serializer.data["inputs"],
            "outputs": serializer.data["outputs"],
        })

    @action(detail=True, methods=["patch"], url_path="results-update")
    def results_patch(self, request, pk=None):
        """Update inputs and regenerate Schedule J Calculation."""
        dataset = self.get_object()
        serializer = self.get_serializer(dataset, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            results = update_calculations(dataset)
            results_serializer = OutputSerializer(dataset,
                                                  context={"results": results["optimization"],
                                                           "bracket_thresholds": results["bracket_thresholds"]})

            return Response({
                "success": True,
                "message": "Patch successful",
                "form": results_serializer.data["inputs"],
                "outputs": results_serializer.data["outputs"],
            })

        return Response({
            "success": False,
            "errors": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)


class OptimizationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TaxDataSet.objects.annotate(tax_year_count=Count("tax_years")).filter(user=self.request.user).filter(tax_year_count=4)

    def get_serializer_class(self):
        if self.action in ["delete"]:
            return TaxDataSetDetailSerializer
        if self.action in ["update", "patch"]:
            return CalculationEntrySerializer
        if self.action == "list":
            return TaxDataSetSerializer
        if self.action == "retrieve":
            return OutputSerializer
        if self.action == "create":
            return CreateCalculationSerializer

    # def get_object(self):
    #     queryset = self.get_queryset()

    def retrieve(self, request, *args, **kwargs):
        # serializer = self.get_serializer(data=request.data)
        dataset = self.get_object()
        results = update_calculations(dataset)
        serializer = self.get_serializer(dataset,
                                         context={"results": results["optimization"],
                                                  "bracket_thresholds": results["bracket_thresholds"]})
        return Response({
            "success": True,
            "message": "Get Successful",
            "form": serializer.data["inputs"],
            "outputs": serializer.data["outputs"],
        })

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid()
        dataset = serializer.save(user=request.user)

        return Response({
            "success": True,
            "dataset_id": dataset.id,
        }, status=status.HTTP_201_CREATED)

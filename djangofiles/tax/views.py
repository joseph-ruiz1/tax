from django.db.models import Count
from django.views.generic import TemplateView
from django.contrib.auth import login, logout
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

import pickle
from .services import CalculationIteration
from .models import TaxDataSet
from .serializers import UserSerializer, TaxDataSetSerializer, LoginSerializer, UserSerializer, TaxDataSetDetailSerializer, CalculationEntrySerializer, CreateCalculationSerializer, OutputSerializer, UserRegistrationSerializer
from .utils import update_calculations

class IndexView(TemplateView):
    template_name = "tax/index.html"

class AuthViewSet(viewsets.ViewSet):
    """
    Handles authentication
    """
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        """
        Creates session
        """
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            # Create cookie
            login(request, serializer.validated_data) 
            return Response({
                'success': True,
                'message': 'Login successful'
            })
        return Response({
            'success': False,
            'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def register(self, request):
        """
        Create user and logs in
        """
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            login(request, user)
            return Response({
                'success': True,
                'message': 'Registration successful'
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def logout(self, request):
        """
        Ends session
        """
        logout(request)
        return Response({
            'success': True,
            'message': 'Logout successful',
        })
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def check(self, request):
        """
        Check auth status
        """
        if request.user.is_authenticated:
            return Response({
                'authenticated': True,
                'user': UserSerializer(request.user).data
            })
        return Response({
            'authenticated': False
        })
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Get current user's info
        """
        return Response(UserSerializer(request.user).data)

class DataSetViewSet(viewsets.ModelViewSet):
    """
    Dataset dashboard page. Allows for viewing, editing, and deletinghu678. Creates are handled in CalculationEntryView
    """
    queryset = TaxDataSet.objects.all()
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        # Only return those with 4 tax years
        return TaxDataSet.objects.annotate(tax_year_count=Count('tax_years')).filter(user=self.request.user).filter(tax_year_count=4)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TaxDataSetSerializer
        elif self.action == 'retrieve':
            return TaxDataSetDetailSerializer
        elif self.action == 'delete':
            return TaxDataSetDetailSerializer
        elif self.action == 'create_step':
            return CreateCalculationSerializer
        elif self.action == 'new_entry':
            return CalculationEntrySerializer
        elif self.action == 'results_get':
            return OutputSerializer
        elif self.action == 'results_patch':
            return CalculationEntrySerializer
        
    @action(detail=False, methods=['post'], url_path='create')
    def create_step(self, request):
        serializer = self.get_serializer(data={})
        if serializer.is_valid():
            dataset = serializer.save(user=request.user)
            return Response({
                'success': True,
                'dataset_id': dataset.id
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'Dataset Creation failed',
            'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['patch'], url_path='new')
    def new_entry(self, request, pk=None):
        dataset = self.get_object()
        serializer = self.get_serializer(dataset, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                    'success': True,
                    'message': 'Data saved successfully',
                    'dataset': serializer.data,
                })    
        return Response({
            'success': False,
            'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'], url_path='results')
    def results_get(self, request, pk=None):
        dataset = self.get_object()

        results = update_calculations(dataset)

        serializer = self.get_serializer(dataset, context={'results': results})
     
        return Response({
            'success': True,
            'message': 'Get Successful',
            'form': serializer.data['inputs'],
            'outputs': serializer.data['outputs']
        })
    
    @action(detail=True, methods=['patch'], url_path='results-update')
    def results_patch(self, request, pk=None):
        # Can refactor this into a single result method with separate actions for self.method = get/post
        dataset = self.get_object()
        serializer = self.get_serializer(dataset, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
           
           
            results = update_calculations(dataset)
            results_serializer = OutputSerializer(dataset, context={'results': results})
            print(results_serializer.data['inputs'])
            return Response({
                'success': True,
                'message': 'Patch successful',
                'form': results_serializer.data['inputs'],
                'outputs': results_serializer.data['outputs'],
            })
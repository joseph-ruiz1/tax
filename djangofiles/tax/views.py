from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Count
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, FormView, DetailView, UpdateView, View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, logout
from rest_framework import viewsets, status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.decorators import action

from .services import TaxCalculation, ScheduleJOptimization, ScheduleJCalculation, CalculationIteration
from .forms import TaxYearDataFormSet, TaxDataSetForm
from .models import TaxYearData, TaxDataSet, ScheduleJForm
from .serializers import UserSerializer, TaxDataSetSerializer, LoginSerializer, UserSerializer, TaxDataSetDetailSerializer, CalculationEntrySerializer, CreateCalculationSerializer, OutputSerializer
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
        Login endpoint, creates session
        """
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user) # Create cookie
            return Response({
                'success': True,
                'user': UserSerializer(user).data,
                'message': 'Login successful'
            })
        return Response({
            'success': False,
            'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def logout(self, request):
        """
        Logout endpoint, ends session
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

class UserViewSet(viewsets.GenericViewSet):
    """
    View for CRUD operations
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Get current user
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

class DataSetViewSet(viewsets.ModelViewSet):
    """
    Dataset dashboard page. Allows for viewing and deleting. Creates are handled in CalculationEntryView
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
        elif self.action in ['retrieve']:
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
        # Consider making this structure flow into the FE form for validation purposes
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
            update_calculations(dataset, serializer)

            return Response({
                    'success': True,
                    'message': 'Patched Successfully',
                    'dataset': serializer.data,
                })
                
        return Response({
            'success': False,
            'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'], url_path='results')
    def results_get(self, request, pk=None):
        dataset = self.get_object()
        serializer = self.get_serializer(dataset)
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
        update_serializer = self.get_serializer(dataset, data=request.data, partial=True)
        if update_serializer.is_valid():
            update_calculations(dataset, update_serializer)
            results_serializer = OutputSerializer(dataset)
            return Response({
                'success': True,
                'message': 'Patch successful',
                'form': results_serializer.data['inputs'],
                'outputs': results_serializer.data['outputs'],
            })

class CalculationEntryView(generics.CreateAPIView):
    """
    Inputs TaxDataSet and four TaxYearData instances
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CalculationEntrySerializer

class RegisterView(FormView):
    template_name = "tax/register.html"
    form_class = UserCreationForm
    success_url = reverse_lazy('tax:dashboard')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

class DashboardView(LoginRequiredMixin, ListView):
    model = TaxDataSet
    template_name = "tax/dashboard.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["taxdata_sets"] = TaxDataSet.objects.filter(user=self.request.user)
        return context
        

class StartNewDataSetView(LoginRequiredMixin, CreateView):
    form_class = TaxDataSetForm
    template_name = "tax/inputscreate.html"

    def form_valid(self, form):
        form.instance.user = self.request.user
        item = form.save()
        self.pk = item.pk
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('tax:inputs', kwargs={'dataset_pk': self.pk})



class InputsCreateView(LoginRequiredMixin, View):
    
    template_name = "tax/inputs.html"
    context_object_name = "inputs"
    
    # Override default get and post, since we are dealing with a formset
    def get(self, request, dataset_pk):
        """
        Retrieve user and dataset roots based on IDs, create new formset and render 
        """
        user = request.user
        dataset = get_object_or_404(TaxDataSet, pk=dataset_pk, user=user)

        # Create formset instance with TaxYearData as base
        formset = TaxYearDataFormSet(queryset=TaxYearData.objects.none())
        return render(request, self.template_name, {
            "formset": formset,
            "user": user,
            "dataset": dataset,
                      })
    
    def post(self, request, dataset_pk):
        """
        Retrieve user and dataset roots based on IDs and place the POSTed formset in DB
        """
        user = request.user
        dataset = get_object_or_404(TaxDataSet, pk=dataset_pk)

        # Retrieves the formset we created and passed in
        formset = TaxYearDataFormSet(request.POST)

        if formset.is_valid():
            # Saves each individual form instance into list so we can link to DataSet
            instances = formset.save(commit=False)
            for instance in instances:
                # Links each TaxData form ForeignKey to TaxDataSet
                instance.dataset = dataset
                # Save to database
                instance.save()

                # Run baseline calculation
                TaxCalculation(instance).calculate()
                instance.save()

            # REROUTE TO RESULTS ONCE THAT IS FINISHED
            return redirect("tax:output", dataset_pk=dataset.pk)

        return render(request, self.template_name, {
            "formset": formset,
            "user": user,
            "dataset": dataset,
        })

class OutputView(LoginRequiredMixin, View):
   template_name = "tax/output.html"
   def get(self, request, dataset_pk):
        user = request.user
        dataset = get_object_or_404(TaxDataSet, pk=dataset_pk, user=user)
        elected_farm_income = dataset.max_elected_farm_income
        qualified_farm_income = dataset.qualified_farm_income
        
        i = CalculationIteration.objects.filter(dataset__pk=dataset.pk, dataset__user=user).count()
        if not i:
            years = TaxYearData.objects.filter(dataset__pk=dataset.pk, dataset__user=user).order_by("pk")
            for year in years:
                # Calculations
                TaxCalculation(year).calculate()
                year.save()

            optimize = ScheduleJOptimization(*years, elected_farm_income=elected_farm_income, elected_farm_qualified=qualified_farm_income, dataset=dataset)
            optimize.optimize_sch_j(elected_farm_income, qualified_farm_income)
            
        results = ScheduleJForm.objects.filter(iteration__dataset=dataset)
        best = dataset.return_optimal_amount
        print(best)
        return render(request, self.template_name, {
            'results' : results,
            'best': best,
        })
       
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, FormView, DetailView, UpdateView, View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .services import TaxCalculation, ScheduleJOptimization, ScheduleJCalculation, CalculationIteration
from .forms import TaxYearDataFormSet, TaxDataSetForm
from .models import TaxYearData, TaxDataSet, ScheduleJForm


class IndexView(TemplateView):
    template_name = "tax/index.html"


class LoginView(LoginView):
    template_name = 'tax/login.html'


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
       
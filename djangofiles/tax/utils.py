from itertools import islice
from django.urls import reverse
from django.db import models
from rest_framework import serializers


def build_taxyear_formset_data(data_list, prefix="form", initial_forms=0):
    """
    Generates POST data for four years of the formset using fixed fields:
    year, filing_status, taxable_income, qualified_income.
    """
    total_forms = len(data_list)
    data = {
        f"{prefix}-TOTAL_FORMS": str(total_forms),
        f"{prefix}-INITIAL_FORMS": str(initial_forms),
        f"{prefix}-MIN_NUM_FORMS": "0",
        f"{prefix}-MAX_NUM_FORMS": "1000",
    }

    # Pull only the relevant data
    fields = ["year", "filing_status", "taxable_income", "qualified_income"]

    for i, item in enumerate(data_list):
        for field, value in zip(fields, item):
            data[f"{prefix}-{i}-{field}"] = value
    return data

def chunker(iterable, size):
    iterator = iter(iterable)
    while True:
        chunk = tuple(islice(iterator, size))
        if not chunk:
            break
        yield chunk


def load_tax_dataset_and_years(self, years: list, sets: int):
    for i, year in enumerate(years):
        response = self.client.get(reverse("tax:start-dataset"))

        self.assertEqual(response.status_code, 302)
        redirect_url = response["Location"]

        self.assertIn("/datasets/", redirect_url, "Invalid Redirect")

        input_url = redirect_url
        tax_data_inputs = [
            (2024, "single", 100000, 40000,),
            (2023, "MFJ", 20000, 100,),
            (2022, "MFJ", 2000, 50,),
            (2021, "single", 100000, 10000,),
        ]
        
        formset_data = build_taxyear_formset_data(tax_data_inputs)

        response = self.client.post(input_url, formset_data, follow=True)


def create_schedulej_fields():
    fields = {}
    for n in range(1, 24):
        fields[f'line_{n}'] = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    for ch in 'abc':
        fields[f'line_2{ch}'] = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    return fields


def validate_tax_years(dataset: object):
    """
    Take in dataset object. Validates there are only 4 years
    """
    from .models import TaxYearData

    years = TaxYearData.objects.filter(dataset=dataset).order_by("-year")

    if years.count() != 4:
        raise serializers.ValidationError("Number of tax year instances not equal to 4")
    return dataset



def update_calculations(dataset, serializer):
    from .services import TaxCalculation, ScheduleJOptimization

    updated_dataset = serializer.save()
    years = updated_dataset.tax_years.all().order_by('-year')

    # Base Calculations
    for tax_year in years:    
        TaxCalculation(tax_year).calculate()
        tax_year.save()

    optimize = ScheduleJOptimization(*years, 
                                        elected_farm_income=updated_dataset.max_elected_farm_income, 
                                        elected_farm_qualified=updated_dataset.qualified_farm_income, 
                                        dataset=updated_dataset)
    optimize.optimize_sch_j(updated_dataset.max_elected_farm_income, updated_dataset.qualified_farm_income)

    return dataset, serializer, optimize

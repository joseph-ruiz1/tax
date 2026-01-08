from itertools import islice

from django.db import models
from django.urls import reverse
from rest_framework import serializers

from .models import TaxDataSet, TaxYearData


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

    years = TaxYearData.objects.filter(dataset=dataset).order_by("-year")

    if years.count() != 4:
        raise serializers.ValidationError("Number of tax year instances not equal to 4")
    return dataset

def sort_tax_years_list(years: list[TaxYearData]) -> list[TaxYearData]:
    sorted_years = sorted(years, key=lambda year: year.year, reverse=True)
    return sorted_years

def update_calculations(dataset: TaxDataSet):
    """
    Helper function to run Schedule J optimization.

    Arguments:
        dataset (TaxDataSet): Years get extracted in function

    Returns:
        dict with: 'optimize' (ScheduleJOptimization): Schedule J optimization results
        'thresholds': dict with bracket thresholds for each year 

    """
    from .services import ScheduleJOptimization, TaxCalculation, find_bracket_thresholds

    years = dataset.tax_years.all().order_by("-year")

    # Base Calculations and bracket finder
    for tax_year in years:
        TaxCalculation(tax_year).calculate()
        tax_year.save()

    optimization_results = ScheduleJOptimization(years,
                                    elected_farm_income=dataset.max_elected_farm_income, 
                                    elected_farm_qualified=dataset.qualified_farm_income, 
                                    ).optimize_sch_j(dataset.max_elected_farm_income, dataset.qualified_farm_income)

    tax_years_with_max_elected = optimization_results['all_elected'].tax_years
    tax_years_with_none_elected = optimization_results['none_elected'].tax_years

    bracket_thresholds = {}
    # Set up structure for find_bracket_thresholds() and iterate through each year
    for year, none_elected_tax_year in tax_years_with_none_elected.items():
        all_elected_tax_year = tax_years_with_max_elected[year]

        rates = [none_elected_tax_year.ordinary_rate, all_elected_tax_year.ordinary_rate]

        bracket_thresholds[year] = find_bracket_thresholds(
            year=year,
            filing_status=none_elected_tax_year.filing_status,
            ordinary_rate_lowest=str(min(rates)),
            ordinary_rate_highest=str(max(rates)),
        )

    return {
        'optimization': optimization_results['optimization_results'],
        'bracket_thresholds': bracket_thresholds
    }
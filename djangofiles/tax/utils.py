from itertools import islice

from django.db import models
from rest_framework import serializers

from .models import TaxDataSet, TaxYearData


def chunker(iterable, size):
    iterator = iter(iterable)
    while True:
        chunk = tuple(islice(iterator, size))
        if not chunk:
            break
        yield chunk

def create_schedulej_fields():
    fields = {}
    for n in range(1, 24):
        fields[f"line_{n}"] = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    for ch in "abc":
        fields[f"line_2{ch}"] = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    return fields

def validate_only_four_tax_years(dataset: object):
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

    sorted_years = sort_tax_years_list(dataset.tax_years.all())

    # Base Calculations and bracket finder
    for tax_year in sorted_years:
        TaxCalculation(tax_year).calculate()
        tax_year.save()

    optimization_results = ScheduleJOptimization(sorted_years,
                                    elected_farm_income=dataset.max_elected_farm_income, 
                                    elected_farm_qualified=dataset.qualified_farm_income, 
                                    ).optimize_sch_j(dataset.max_elected_farm_income, dataset.qualified_farm_income)

    tax_years_with_max_elected = optimization_results["all_elected"].tax_years
    tax_years_with_none_elected = optimization_results["none_elected"].tax_years

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
        "optimization": optimization_results["optimization_results"],
        "bracket_thresholds": bracket_thresholds,
    }

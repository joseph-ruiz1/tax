from itertools import islice
from typing import TYPE_CHECKING

from django.db import models
from rest_framework import serializers

from .models import TaxDataSet, TaxYearData

if TYPE_CHECKING:
    from .services import ScheduleJResultsContainer

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

def validate_years_are_in_order(years: list[TaxYearData | dict]):
    """Ensure years are not skipped, e.g. 2024, 2023, 2021, 2020 would fail."""
    for i in range(len(years) - 1):
        current_year = getattr(years[i], "year", None) or years[i].get("year")
        next_year = getattr(years[i+1], "year", None) or years[i+1].get("year")

        if current_year < next_year:
            raise serializers.ValidationError("Years must be in descending order")

def sort_tax_years_list(years: list[TaxYearData]) -> list[TaxYearData]:
    sorted_years = sorted(years, key=lambda year: year.year, reverse=True)
    return sorted_years

def update_calculations(dataset: TaxDataSet):
    from .services import ScheduleJOptimizer, TaxCalculation, ScheduleJConfig

    sorted_years = sort_tax_years_list(dataset.tax_years.all())

    # Base Calculations and bracket finder
    for tax_year in sorted_years:
        TaxCalculation(tax_year).calculate_total_tax()
        tax_year.save()

    config = ScheduleJConfig()
    optimization_results = ScheduleJOptimizer(sorted_years,
                                    max_elected_farm_income=dataset.max_elected_farm_income,
                                    qualified_farm_income=dataset.qualified_farm_income,
                                    config=config,
                                    ).run_optimization()

    all_elected_instance = optimization_results.all_elected_instance
    none_elected_instance = optimization_results.none_elected_instance
    bracket_thresholds = handle_bracket_thresholds(all_elected_instance, none_elected_instance)

    return {
        "optimization": optimization_results.calculation_iterations,
        "bracket_thresholds": bracket_thresholds,
    }

# Need to figure out services import
def handle_bracket_thresholds(all_elected_instance: ScheduleJResultsContainer, none_elected_instance: ScheduleJResultsContainer):
    from .services import find_bracket_thresholds

    print(all_elected_instance.schedule_j_form.taxable_ordinary_results)
    print(none_elected_instance.schedule_j_form.taxable_ordinary_results)
    tax_years = none_elected_instance.tax_years  # Both instances will have same years/filing status

    bracket_thresholds = {}
    for year, year_obj in tax_years.items():
        all_elected_rate = all_elected_instance.schedule_j_form.taxable_ordinary_results[year]["ordinary_rate"]
        none_elected_rate = none_elected_instance.schedule_j_form.taxable_ordinary_results[year]["ordinary_rate"]

        bracket_thresholds[year] = find_bracket_thresholds(
            year=year,
            filing_status=year_obj.filing_status,
            ordinary_rate_lowest=str(min(all_elected_rate, none_elected_rate)),
            ordinary_rate_highest=str(max(all_elected_rate, none_elected_rate)),
        )

    return bracket_thresholds

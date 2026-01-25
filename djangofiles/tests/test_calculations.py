import pytest
from calculation_cases import (
    BASIC_TAX_CALCULATION_INPUTS,
    EXPECTED_OUTPUTS_BASIC_TAX_CALC,
    EXPECTED_OUTPUTS_SORTED_YEARS,
)
from tax.models import TaxDataSet, TaxYearData, User
from tax.services import (
    IncomeDistributor,
    ScheduleJCalculation,
    ScheduleJConfig,
    ScheduleJOptimizer,
    TaxCalculation,
    find_bracket_thresholds,
)
from tax.utils import sort_tax_years_list
from utils.calculation_utils import (
    build_test_cases,
    calculate_total_tax_all_years,
)


@pytest.mark.parametrize(
    "inputs, expected",
    build_test_cases(BASIC_TAX_CALCULATION_INPUTS, EXPECTED_OUTPUTS_BASIC_TAX_CALC, "tax_calculation"),
)
def test_basic_tax_calculation(create_models_for_test_cases, inputs, expected):
    for case, sorted_years in create_models_for_test_cases([inputs]):
        tax_results_all_years = calculate_total_tax_all_years(sorted_years)

        for field_name, expected_value in expected.items():
            assert tax_results_all_years[field_name] == expected_value

@pytest.mark.parametrize(
    "inputs, expected",
    build_test_cases(BASIC_TAX_CALCULATION_INPUTS, EXPECTED_OUTPUTS_SORTED_YEARS, "sort_years"),
)
def test_year_sorting(create_unsorted_models_for_test_cases, inputs, expected):
    for case, unsorted_years in create_unsorted_models_for_test_cases([inputs]):
        sorted_years_objs = sort_tax_years_list(unsorted_years)
        sorted_years = [y.year for y in sorted_years_objs]

        for expected_value in expected.values():
            assert sorted_years == expected_value

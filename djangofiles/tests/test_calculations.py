import pytest
from calculation_cases import (
    BASIC_TAX_CALCULATION_INPUTS,
    EXPECTED_OUTPUT_INCOME_ALLOCATION,
    EXPECTED_OUTPUT_CREATE_MAP,
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

@pytest.mark.parametrize(
    "inputs, expected",
    build_test_cases(BASIC_TAX_CALCULATION_INPUTS, EXPECTED_OUTPUT_CREATE_MAP, "create_map"),
)
class TestScheduleJTaxYearMapping:
    @pytest.fixture
    def sch_j_instance(self, create_sch_j_instance, inputs):
        return create_sch_j_instance(inputs)

    def test_tax_year_map_creation(self, sch_j_instance, expected):
        tax_year_map = sch_j_instance.tax_years
        expected_years = expected["years"]

        for (actual_year, year_obj), expected_year in zip(tax_year_map.items(), expected_years, strict=False):
            assert actual_year == expected_year
            assert isinstance(year_obj, TaxYearData)

    def test_retrieval_of_first_year(self, sch_j_instance, expected):
        first_year = sch_j_instance.election_year
        first_year_obj = sch_j_instance.election_year_obj
        expected_year = expected["years"][0]

        assert first_year == expected_year
        assert isinstance(first_year_obj, TaxYearData)

@pytest.mark.parametrize(
    "inputs, expected",
    build_test_cases(BASIC_TAX_CALCULATION_INPUTS, EXPECTED_OUTPUT_INCOME_ALLOCATION, "allocate_income"),
)
def test_income_allocation(create_models_for_test_cases, create_sch_j_instance, inputs, expected):
    distributor = IncomeDistributor(create_sch_j_instance(inputs).tax_years)
    distributor.distribute_all_elected_income()

    for i, year_obj in enumerate(distributor.adjusted_years.values()):
        assert round(year_obj.taxable_income) == expected["allocated_taxable_income"][i]
        assert round(year_obj.qualified_income) == expected["allocated_qualified_income"][i]


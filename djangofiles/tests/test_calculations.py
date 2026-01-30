from decimal import Decimal

import pytest
from calculation_cases import (
    BASIC_TAX_CALCULATION_INPUTS,
    EXPECTED_OUTPUT_SCHEDULE_J,
    EXPECTED_OUTPUTS_BASIC_TAX_CALC,
    EXPECTED_OUTPUTS_BRACKET_THRESHOLDS,
    EXPECTED_OUTPUTS_FULL_SCH_J_CALC,
    EXPECTED_OUTPUTS_OPTIMIZATION,
    EXPECTED_OUTPUTS_SORTED_YEARS,
)
from tax.models import TaxDataSet, TaxYearData
from tax.services import (
    IncomeDistributor,
    ScheduleJCalculation,
    ScheduleJConfig,
    ScheduleJForm,
    ScheduleJOptimizer,
    TaxCalculation,
    find_bracket_thresholds,
)
from tax.utils import sort_tax_years_list, update_calculations, handle_bracket_thresholds
from utils.calculation_utils import (
    _run_sch_j_tax_assignment,
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
    build_test_cases(BASIC_TAX_CALCULATION_INPUTS, EXPECTED_OUTPUT_SCHEDULE_J, "create_map"),
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
    build_test_cases(BASIC_TAX_CALCULATION_INPUTS, EXPECTED_OUTPUT_SCHEDULE_J, "allocate_income"),
)
def test_income_allocation(create_models_for_test_cases, create_sch_j_instance, inputs, expected):
    distributor = IncomeDistributor(create_sch_j_instance(inputs).tax_years)
    distributor.distribute_all_elected_income()

    for i, year_obj in enumerate(distributor.adjusted_years.values()):
        assert round(year_obj.taxable_income) == expected["allocated_taxable_income"][i]
        assert round(year_obj.qualified_income) == expected["allocated_qualified_income"][i]

@pytest.mark.parametrize(
    "inputs, expected",
    build_test_cases(BASIC_TAX_CALCULATION_INPUTS, EXPECTED_OUTPUT_SCHEDULE_J, "tax_assignment"),
)
def test_sch_j_yearly_tax_assignment(create_models_for_test_cases, create_sch_j_instance, create_sch_j_config, inputs, expected):
    """Tests _adjust_taxable_income_by_elected(), _fill_form_with_tax_results(), """
    config = create_sch_j_config(show_full_sch_j_form=True)
    instance = create_sch_j_instance(inputs, config)

    filtered_form = _run_sch_j_tax_assignment(instance, use_adjusted=False)
    assert filtered_form == expected

@pytest.mark.parametrize(
    "inputs, expected",
    build_test_cases(BASIC_TAX_CALCULATION_INPUTS, EXPECTED_OUTPUT_SCHEDULE_J, "adj_tax_assignment"),
)
def test_adj_sch_j_yearly_tax_assignment(create_models_for_test_cases, create_sch_j_instance, create_sch_j_config, inputs, expected):
    """Tests _adjust_taxable_income_by_elected(), _fill_form_with_adj_tax_results(),"""
    config = create_sch_j_config(show_full_sch_j_form=True)
    instance = create_sch_j_instance(inputs, config)

    filtered_form = _run_sch_j_tax_assignment(instance, use_adjusted=True)
    assert filtered_form == expected

@pytest.mark.parametrize(
    "inputs, expected",
    build_test_cases(BASIC_TAX_CALCULATION_INPUTS, EXPECTED_OUTPUTS_FULL_SCH_J_CALC, "full_sch_j_calc"),
)
def test_full_sch_j_calculation(create_models_for_test_cases, create_sch_j_instance, create_sch_j_config, inputs, expected):
    config = create_sch_j_config(show_full_sch_j_form=True)
    instance = create_sch_j_instance(inputs, config)

    results = instance.calculate()

    sch_j_form = results.schedule_j_form.to_dict()

    for line, result in sch_j_form.items():
        assert round(result) == expected[line]

@pytest.mark.parametrize(
        "inputs, expected",
        build_test_cases(BASIC_TAX_CALCULATION_INPUTS, EXPECTED_OUTPUTS_OPTIMIZATION, "income_proportion"),
    )
class TestOptimizationHelpers:
    @pytest.fixture
    def optimization_instance(self, create_optimization_instance, inputs):
        return create_optimization_instance(inputs)

    def test_sch_j_optimization_income_proportion(self, optimization_instance, expected):
        ordinary_percentage, qualified_percentage = optimization_instance._calculate_income_proportions()

        assert ordinary_percentage == expected["ordinary_percentage"]
        assert qualified_percentage == expected["qualified_percentage"]

    def test_sch_j_config_creation(self, optimization_instance, expected):
        config_obj = optimization_instance._create_sch_j_config_showing_all_years()
        assert not config_obj.show_full_sch_j_form
        assert config_obj.show_all_tax_years

@pytest.mark.parametrize(
    "inputs, expected",
    build_test_cases(BASIC_TAX_CALCULATION_INPUTS, EXPECTED_OUTPUTS_OPTIMIZATION, "first_and_last_instances"),
)
class TestFirstandLastInstances:
    @pytest.fixture
    def optimization_instance(self, create_optimization_instance, inputs):
        return create_optimization_instance(inputs)

    def test_first_instance(self, optimization_instance, expected):
        max_elected_farm_income = optimization_instance.max_elected_farm_income
        qualified_farm_income = optimization_instance.qualified_farm_income

        sch_j_results = optimization_instance._handle_first_iteration(max_elected_farm_income, qualified_farm_income)

        assert sch_j_results.show_all_tax_years
        assert not sch_j_results.show_full_sch_j_form
        assert round(sch_j_results.schedule_j_form.line_23) == expected["first_instance"]["line_23"]

    def test_last_instance(self, optimization_instance, expected):
        _ordinary_percentage, qualified_percentage = optimization_instance._calculate_income_proportions()

        sch_j_results = optimization_instance._handle_last_iteration(Decimal(500), 500 * qualified_percentage)

        assert sch_j_results.show_all_tax_years
        assert not sch_j_results.show_full_sch_j_form
        assert round(sch_j_results.schedule_j_form.line_23) == expected["last_instance"]["line_23"]

@pytest.mark.parametrize(
    "inputs, expected",
    build_test_cases(BASIC_TAX_CALCULATION_INPUTS, EXPECTED_OUTPUTS_OPTIMIZATION, "complete_optimization"),
)
def test_complete_optimization(inputs, expected, create_optimization_instance):
    optimizer = create_optimization_instance(inputs)
    results = optimizer.run_optimization()

@pytest.mark.parametrize(
    "inputs, expected",
    build_test_cases(BASIC_TAX_CALCULATION_INPUTS, EXPECTED_OUTPUTS_OPTIMIZATION, "complete_optimization"),
)
def test_update_calculations_entry(inputs, expected, create_models_for_test_cases):
    for case, years in create_models_for_test_cases([inputs]):
        results = update_calculations(case["dataset_instance"])
        print(results["bracket_thresholds"])

@pytest.mark.parametrize(
    "inputs, expected",
    build_test_cases(BASIC_TAX_CALCULATION_INPUTS, EXPECTED_OUTPUTS_BRACKET_THRESHOLDS, "bracket_thresholds"),
)
def test_bracket_thresholds(inputs, expected, run_optimization_instance):
    test = run_optimization_instance(inputs)
    results = handle_bracket_thresholds(test)

    assert results == expected["brackets"]

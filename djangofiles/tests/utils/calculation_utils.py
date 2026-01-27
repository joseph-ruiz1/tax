from collections.abc import Mapping

import pytest
from tax.models import TaxYearData
from tax.services import TaxCalculation, TaxCalculationResult
from tax.utils import sort_tax_years_list
from utils.typing_utils import TestCaseInputs, TestCaseOutputs


def calculate_total_tax_all_years(years: list[TaxYearData]) -> Mapping[str, TaxCalculationResult]:
    results = []
    for year_obj in years:
        tax_result = TaxCalculation(year_obj).calculate_total_tax()
        results.append(round(tax_result.total_tax))
    return {"total_tax": results}


def build_test_cases(test_case_inputs: TestCaseInputs, test_case_expected_outputs: TestCaseOutputs, item_to_test: str) -> list[tuple]:
    """Build test cases for a specific item that we want to test."""
    if item_to_test not in test_case_expected_outputs:
        raise ValueError(f"item_to_test='{item_to_test}' not found in expected outputs")

    test_cases = []
    item_scenarios = test_case_expected_outputs[item_to_test]

    for scenario_name, expected_output_data in item_scenarios.items():
        if scenario_name not in test_case_inputs:
            raise KeyError(f"Scenario '{scenario_name}' found in expected outputs but not in inputs")

        test_cases.append(
            pytest.param(
                test_case_inputs[scenario_name],
                expected_output_data,
                id=scenario_name,
            ),
        )

    return test_cases

def _run_sch_j_tax_assignment(instance, use_adjusted: bool = False) -> Mapping[str, int]:
    if use_adjusted:
        instance._adjust_taxable_income_by_elected()
        tax_for_each_year = instance._calculate_tax_on_all_years()
        instance._fill_form_with_adj_tax_results(tax_for_each_year)
    else:
        tax_for_each_year = instance._calculate_tax_on_all_years()
        instance._fill_form_with_tax_results(tax_for_each_year)

    return {k: round(v) for k, v in instance.sch_j.to_dict().items() if v is not None}

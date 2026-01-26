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

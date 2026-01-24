import pytest
from tax.services import TaxCalculation


def calculate_total_tax_all_years(years):
    results = []
    for year_obj in years:
        tax_result = TaxCalculation(year_obj).calculate_total_tax()
        results.append(round(tax_result.total_tax))
    return {"total_tax": results}


def build_test_cases(inputs: dict, expected_outputs: dict, item_to_test: str) -> ():
    """Build test cases for a specific calculation type."""
    test_cases = []

    for scenario_name in expected_outputs.keys():
        if scenario_name not in inputs:
            raise KeyError(f"Scenario '{scenario_name}' found in expected outputs but not in inputs")

        inputs = inputs[scenario_name]
        expected = expected_outputs[scenario_name][item_to_test]

        test_cases.append(
            pytest.param(
                inputs,
                expected,
                id=scenario_name,
            ),
        )
    return test_cases

from collections.abc import Mapping

from typing_extensions import TypedDict


class TaxYearDataInputs(TypedDict):
    year: int
    filing_status: str
    taxable_income: int
    qualified_income: int
    is_electing: bool
    elected_farm_income: int
    qualified_farm_income: int

class DatasetInfo(TypedDict):
    name: str
    max_elected_farm_income: int
    qualified_farm_income: int
    election_year: str

class CalculationScenarioInput(TypedDict):
    dataset: DatasetInfo
    inputs: list[TaxYearDataInputs]

class CalculationScenarioOutput(TypedDict):
    tax_calculation: Mapping[str, list[int]]

TestCaseInputs = Mapping[str, CalculationScenarioInput]
TestCaseOutputs = Mapping[str, CalculationScenarioOutput]

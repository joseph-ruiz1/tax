from types import FunctionType
from dataclasses import replace

import pytest
from calculation_cases import BASIC_TAX_CALCULATION_INPUTS
from django.test import Client
from tax.models import TaxDataSet, TaxYearData, User
from tax.services import ScheduleJCalculation, ScheduleJConfig
from tax.utils import sort_tax_years_list
from utils.typing_utils import CalculationScenarioInput


@pytest.fixture
def test_user(db):
    return User.objects.create_user(username="test", password="testing")

@pytest.fixture
def authenticated_client(test_user):
    client = Client()
    client.login(username="test", password="testing")
    return client

@pytest.fixture
def create_tax_models():
    """Factory fixture to create TaxDataSet and TaxYearData instances."""
    def _create(test_cases: CalculationScenarioInput, user: User):
        processed_cases = []
        for i, case in enumerate(test_cases, start=1):
            dataset_info = case.get("dataset", {})
            dataset_name = dataset_info.get("name", f"Test Dataset {i}")
            dataset_fields = dataset_info.copy()
            dataset_fields["name"] = dataset_name
            dataset = TaxDataSet(**dataset_fields, user=user)
            dataset.save()
            dataset.refresh_from_db()

            raw_inputs = case.get("inputs", [])
            instances = []

            for entry in raw_inputs:
                if isinstance(entry, dict):
                    obj = TaxYearData(dataset=dataset, **entry)
                elif isinstance(entry, (list, tuple)):
                    if len(entry) != 7:
                        msg = f"Expected 7 values per list, got {len(entry)} → {entry}"
                        raise ValueError(msg)
                    year, filing_status, taxable_income, qualified_income, is_electing, elected_farm_income, qualified_farm_income = entry
                    obj = TaxYearData(
                        dataset=dataset,
                        year=year,
                        filing_status=filing_status,
                        taxable_income=taxable_income,
                        qualified_income=qualified_income,
                        is_electing=bool(is_electing),
                        elected_farm_income=elected_farm_income,
                        qualified_farm_income=qualified_farm_income,
                    )
                else:
                    msg = f"Expected dict or list, got {type(entry)}"
                    raise TypeError(msg)

                obj.save()
                instances.append(obj)

            case_copy = case.copy()
            case_copy["dataset_instance"] = dataset
            case_copy["inputs"] = instances
            processed_cases.append(case_copy)

        return processed_cases

    return _create

@pytest.fixture
def create_models_for_test_cases(test_user: FunctionType, create_tax_models: FunctionType):
    def _setup(test_cases):
        processed_cases = create_tax_models(test_cases, test_user)

        for case in processed_cases:
            unsorted_years_list = case["dataset_instance"].tax_years.all()
            sorted_years_list = sort_tax_years_list(unsorted_years_list)

            yield case, sorted_years_list
    return _setup

@pytest.fixture
def create_unsorted_models_for_test_cases(test_user: FunctionType, create_tax_models: FunctionType):
    def _setup(test_cases):
        processed_cases = create_tax_models(test_cases, test_user)

        for case in processed_cases:
            unsorted_years_list = case["dataset_instance"].tax_years.all()

            yield case, unsorted_years_list
    return _setup

@pytest.fixture
def create_sch_j_config():
    def _create(**kwargs):
        base = ScheduleJConfig()
        if kwargs:
            return replace(base, **kwargs)
        return base
    return _create

@pytest.fixture
def create_sch_j_instance(create_models_for_test_cases, create_sch_j_config):
    def _create(inputs: CalculationScenarioInput, config: ScheduleJConfig = None):
        if config is None:
            config = create_sch_j_config()

        for case, years in create_models_for_test_cases([inputs]):
            return ScheduleJCalculation(
                years,
                case["dataset_instance"].max_elected_farm_income,
                case["dataset_instance"].qualified_farm_income,
                config,
            )
        return None
    return _create

import unittest
from decimal import Decimal

from django.test import TestCase
from rest_framework.test import APITestCase

from .models import TaxDataSet, TaxYearData, User
from .serializers import OutputSerializer
from .services import (
    IncomeDistributor,
    ScheduleJCalculation,
    ScheduleJConfig,
    ScheduleJOptimizer,
    TaxCalculation,
    find_bracket_thresholds,
)
from .utils import sort_tax_years_list


# HELPER FUNCTIONS
def create_taxdataset(user, elected, elected_qualified):
    return TaxDataSet.objects.create(user=user, max_elected_farm_income=elected, qualified_farm_income=elected_qualified)

def create_taxyeardata(year,  # noqa: PLR0913
                        filing_status,
                        taxable_income,
                        qualified_income,
                        is_electing,
                        elected_farm_income,
                        qualified_farm_income,
                        dataset=None) -> TaxYearData:
    return TaxYearData(year=year, filing_status=filing_status, taxable_income=taxable_income,
                                  qualified_income=qualified_income, is_electing=is_electing,
                                  elected_farm_income=elected_farm_income,
                                  qualified_farm_income=qualified_farm_income, dataset=dataset)

def create_dataset_with_tax_years(user, tax_year_inputs: tuple, elected, elected_qualified):
    dataset = create_taxdataset(user, elected, elected_qualified)
    for tax_year in tax_year_inputs:
        year, filing_status, taxable_income, qualified_income, is_electing, elected_farm_income, qualified_farm_income = tax_year

        TaxYearData.objects.create(
            dataset=dataset,
            year=year,
            filing_status=filing_status,
            taxable_income=taxable_income,
            qualified_income=qualified_income,
            is_electing=is_electing,
            elected_farm_income=elected_farm_income,
            qualified_farm_income=qualified_farm_income
        )
    return dataset

def create_test_user(username, password):
    return User.objects.create_user(username=username, password=password)

def create_several_test_users(username, password):
    return User.objects.create_user(username=username, password=password)

def create_tax_year_data_list(test_cases, user, save=True):
    """
    Creates TaxDataSet instances for each test case. Creates TaxYearData instances for each case and attaches dataset.

    Sample input:
        SCHEDULE_J_ALLOCATION_TEST = [
            {'inputs': [
                dict(year=2024, filing_status='MFJ', taxable_income=120000, qualified_income=105000,
                     is_electing=True, elected_farm_income=10000, qualified_farm_income=0),
                dict(year=2023, filing_status='MFJ', taxable_income=85000, qualified_income=70000,
                     is_electing=True, elected_farm_income=20000, qualified_farm_income=1000),
            ],
            'outputs': [143, 2812],
            'dataset': dict(name='test', max_elected_farm_income=10000, qualified=0)}
        ],

    Also supports compact list style:
        [
            [2024, 'MFJ', 120000, 105000, True, 10000, 0],
            ...
        ]

    Args:
        test_cases (list): list of dicts or lists describing TaxYearData.
        save (bool): whether to save the instances to the database (default True).

    Returns:
        list[TaxYearData]: list of created instances.

    Example:
            [{'inputs': [TaxYearDatas], 'outputs': [], 'dataset': {dataset inputs}, 'dataset_instance': TaxDataSet}]

    """
    processed_cases = []
    for i, case in enumerate(test_cases, start=1):
        # Create dataset
        dataset_info = case.get("dataset", {})
        dataset_name = dataset_info.get("name", f"Test Dataset {i}")
        dataset_fields = dataset_info.copy()
        dataset_fields["name"] = dataset_name  # ensure name is included

        dataset = TaxDataSet(**dataset_fields, user=user)
        if save:
            dataset.save()
            # Get the Decimal typing instead of int
            dataset.refresh_from_db()

        # Create TaxYearData instances linked to dataset
        raw_inputs = case.get("inputs", [])
        instances = []

        for entry in raw_inputs:
            if isinstance(entry, dict):
                obj = TaxYearData(dataset=dataset, **entry)
            elif isinstance(entry, (list, tuple)):
                if len(entry) != 7:
                    raise ValueError(f"Expected 7 values per list, got {len(entry)} → {entry}")
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
                raise TypeError(f"Expected dict or list, got {type(entry)}")

            if save:
                obj.save()
            instances.append(obj)

        case_copy = case.copy()
        case_copy["dataset_instance"] = dataset
        case_copy["inputs"] = instances
        processed_cases.append(case_copy)

    return processed_cases

# TESTS
class TestUserModel(TestCase):
    def test_create_single_user(self):
        test_user = create_test_user(username="test", password="testing123")
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(test_user.username, "test")
        self.assertEqual(test_user.id, 1)

    def test_create_several_users(self):
        users = [create_several_test_users(username, password) for username, password in CREDENTIALS]

        self.assertEqual(User.objects.count(), len(CREDENTIALS))

        expected_ids = list(range(1, len(users) + 1))
        actual_ids = [user.id for user in users]
        self.assertEqual(actual_ids, expected_ids)

class BasicTaxCalculationTest(TestCase):
    def setUp(self):
        self.test_user = create_test_user(username="test", password="testing")
        self.client.login(username="test", password="testing")

    def test_calculation(self):
        for i, test in enumerate(TEST_CASES_BASIC_TAX_CALC):
            dataset = create_dataset_with_tax_years(self.test_user, test["inputs"], 0, 0)
            total_tax_results = []

            for tax_year in TaxYearData.objects.filter(dataset=dataset):
                try:
                    tax_results = TaxCalculation(tax_year).calculate_total_tax()
                except TypeError as e:
                    print(f"❌ Test {i}: Incorrect input type - {e}")
                    tax_results = None
                except ValueError as e:
                    print(f"❌ Test {i}: Invalid input value - {e}")
                    tax_results = None

                total_tax_results.append(tax_results)

            for j, (result, expected) in enumerate(zip(total_tax_results, test["outputs"], strict=True), start=1):
                if round(result.total_tax) != expected:
                    print(f"❌ Test {i}, Year {j}: Got {result.total_tax}, expected {expected}")

class BasicTaxCalculationTestOlderYears(TestCase):
    """Run base TaxCalculation to test 2021-2018. Results should match TEST outputs."""

    def setUp(self):
        self.test_user = create_test_user(username="test", password="testing")
        self.client.login(username="test", password="testing")

    def test_base_tax_calculations(self):
        for i, test in enumerate(TEST_CASES_BASIC_TAX_CALC_OLDER_YEARS):
            dataset = create_dataset_with_tax_years(self.test_user, test["inputs"], 0, 0)

            total_tax_results = []

            for tax_year in TaxYearData.objects.filter(dataset=dataset):
                tax_calc_result = TaxCalculation(tax_year).calculate_total_tax()
                total_tax_results.append(round(tax_calc_result.total_tax))

            for j, (result, expected) in enumerate(zip(total_tax_results, test["outputs"], strict=False)):
                if round(result) != expected:
                    print(f"❌ Test {i}, Year {j}: Got {result}, expected {expected}")

class ScheduleJCalculationTest(TestCase):
    """Runs Schedule J calculation in full. Compare ScheduleJForm to outputs in SCHEDULE_J_ALLOCATION_TEST."""

    def setUp(self):
        self.test_user = create_test_user(username="test", password="testing")
        self.client.login(username="test", password="testing")

    def test_serializer_outputs(self):
        test_cases = create_tax_year_data_list(FULL_SCHEDULE_J_CASES, user=self.test_user, save=True)

        for test_number, case in enumerate(test_cases, start=1):
            # Get the dataset instance
            dataset = case["dataset_instance"]
            config = ScheduleJConfig(show_full_sch_j_form=True)

            unsorted_years_list = dataset.tax_years.all()
            sorted_years = sort_tax_years_list(unsorted_years_list)

            elected_income = sorted_years[0].elected_farm_income
            elected_qualified = sorted_years[0].qualified_farm_income

            sch_j_instance = ScheduleJCalculation(sorted_years, elected_income, elected_qualified, config).calculate()

            sch_j_form = sch_j_instance.schedule_j_form.to_dict()

            for (line, result), (expected_line, expected_result) in zip(sch_j_form.items(), case["outputs"].items(), strict=False):
                rounded_result = round(result)
                if rounded_result != expected_result:
                    print(f"wrong output at {line} in test {test_number}: got {rounded_result}, expected {expected_result}")

@unittest.skip("Deprecated test")
class TaxDataSetSerializerTest(APITestCase):
    """
    updated for on demand calculations
    """
    def setUp(self):
        self.test_user = create_test_user(username="test", password="testing")
        self.client.login(username="test", password="testing")

    def test_serializer_outputs(self):
        for i, test in enumerate(SCHEDULE_J_OPTIMIZATION_TEST):
                max_elected, max_qualified_elected = test["elected"]
                dataset = create_dataset_with_tax_years(self.test_user, test['inputs'], max_elected, max_qualified_elected)
                dataset.refresh_from_db()

                years = TaxYearData.objects.filter(dataset=dataset).order_by("-year")

                # Base Calculations
                for year in years:
                    TaxCalculation(year).calculate_total_tax()

        optimize = ScheduleJOptimization(*years, elected_farm_income=dataset.max_elected_farm_income, elected_farm_qualified=dataset.qualified_farm_income, dataset=dataset)
        optimize.optimize_sch_j(dataset.max_elected_farm_income, dataset.qualified_farm_income)

        data = OutputSerializer(dataset).data

@unittest.skip("Hold until logic is refactored")
class FindTaxBracketThresholdsTest(TestCase):
    """
    Test find_bracket_thresholds to ensure 1 bracket below and above is returned based on adjusted_year taxable ordiary income"
    """
    def setUp(self):
        self.test_user = create_test_user(username="test", password="testing")
        self.client.login(username="test", password="testing")

    def test_bracket_thresholds(self):
        test_cases = create_tax_year_data_list(BRACKET_THRESHOLDS_TEST_CASES, user=self.test_user, save=True)
        for test_set in test_cases:
            # Get the dataset instance
            dataset = test_set["dataset_instance"]
            dataset.save()

            # Convert queryset to a list
            years = list(TaxYearData.objects.filter(dataset=dataset).order_by("-year"))

            # Base Calculations
            for year in years:
                TaxCalculation(year).calculate_total_tax()

            results_container = ScheduleJCalculation(years, show_all_years=True).calculate(dataset.max_elected_farm_income, dataset.qualified_farm_income)
            adjusted_years = results_container.tax_years
            # Test each year to see if 1 bracket below and above are returned based on taxable ordinary
            for adjusted_year in adjusted_years.values():
                bracket_threshold_results = find_bracket_thresholds(adjusted_year.year, adjusted_year.filing_status, str(adjusted_year.ordinary_rate), str(adjusted_year.ordinary_rate))
                year = adjusted_year.year

                expected_rates = test_set["results"][year]
                # NEED TO FIGURE OUT HOW TO ONLY RETRIEVE KEYS FROM BRACKET_THRESHOLD_TEST
                # PROB A BETTER WAY TO DO THAT CONVERTING TO LIST
                actual_rates = list(bracket_threshold_results.keys())

                if expected_rates != actual_rates:
                    print(f"Set: {dataset.name}: Rates failed at year {year}: expected {expected_rates}, got {actual_rates}")

class SortTaxYearsUtilFunctionTest(TestCase):
    def setUp(self):
        self.test_user = create_test_user(username="test", password="testing")
        self.client.login(username="test", password="testing")

    def test_sort_function(self):
        test_cases = create_tax_year_data_list(TEST_CASES_UNORGANIZED_YEARS, user=self.test_user, save=True)

        for case in test_cases:
            unsorted_years_list = case["dataset_instance"].tax_years.all()
            sorted_years_list = sort_tax_years_list(unsorted_years_list)

            for i, (result, expected) in enumerate(zip(sorted_years_list, case["outputs"], strict=False), start=1):
                if result.year != str(expected):
                    print(result.year, expected)
                    print(f"❌ Test {i}, Year {result.year}: Got {result.year}, expected {expected}")

class CreateTaxYearsMapTest(TestCase):
    def setUp(self):
        self.test_user = create_test_user(username="test", password="testing")
        self.client.login(username="test", password="testing")

    def test_map_creation(self):
        test_cases = create_tax_year_data_list(TEST_CASES_UNORGANIZED_YEARS, user=self.test_user, save=True)

        for case in test_cases:
            unsorted_years_list = case["dataset_instance"].tax_years.all()
            sorted_years_list = sort_tax_years_list(unsorted_years_list)

            sch_j_instance = ScheduleJCalculation(sorted_years_list, Decimal(1000), Decimal(0), None)
            tax_year_map = sch_j_instance.tax_years

            for i, ((year, year_obj), expected) in enumerate(zip(tax_year_map.items(), case["outputs"], strict=False), start=1):
                assert year == expected, f"Map key ({year}) does not match expected year ({expected}) in test {i}"
                assert isinstance(year_obj, TaxYearData), f"Map value {year_obj} is not a TaxYearData in test {i}"

class IncomeAllocationTest(TestCase):
    def setUp(self):
        self.test_user = create_test_user(username="test", password="testing")
        self.client.login(username="test", password="testing")

    def test_map_creation(self):
        test_cases = create_tax_year_data_list(SCHEDULE_J_INCOME_ALLOCATION_TEST, user=self.test_user, save=True)

        for case in test_cases:
            unsorted_years_list = case["dataset_instance"].tax_years.all()
            sorted_years_list = sort_tax_years_list(unsorted_years_list)

            tax_years_map = {int(y.year): y for y in sorted_years_list}

            distributor = IncomeDistributor(tax_years_map)
            distributor.distribute_all_elected_income()

            for i, ((year, year_obj), expected) in enumerate(zip(distributor.adjusted_years.items(), case["outputs"], strict=False), start=1):
                expected_taxable_income = expected[0]
                expected_qualified_income = expected[1]
                if year_obj.taxable_income != expected_taxable_income:
                    msg = f"Expected taxable income of {expected_taxable_income}, got {year_obj.taxable_income} in test {i}, year {year}"
                    print(msg)
                if year_obj.qualified_income != expected_qualified_income:
                    msg = f"Expected qualified income of {expected_qualified_income}, got {year_obj.qualified_income} in test {i}, year {year}"
                    print(msg)

class GetFirstYearObjectFromTaxYearMap(TestCase):
    def setUp(self):
        self.test_user = create_test_user(username="test", password="testing")
        self.client.login(username="test", password="testing")

    def test_map_creation(self):
        test_cases = create_tax_year_data_list(TEST_CASES_FOR_FIRST_YEAR_MAP, user=self.test_user, save=True)

        for i, case in enumerate(test_cases, start=1):
            unsorted_years_list = case["dataset_instance"].tax_years.all()
            sorted_years_list = sort_tax_years_list(unsorted_years_list)

            sch_j_instance = ScheduleJCalculation(sorted_years_list, Decimal(1000), Decimal(0), None)
            election_year = sch_j_instance.election_year
            election_year_obj = sch_j_instance.election_year_obj
            expected_year = case["outputs"]

            assert election_year == expected_year, f"First year ({election_year}) does not equal the first year ({expected_year}) in test {i}"
            assert isinstance(election_year_obj, TaxYearData), f"First year {election_year_obj} is not a TaxYearData in test {i}"

class ScheduleJYearlyTaxAssignmentTest(TestCase):
    def setUp(self):
        self.test_user = create_test_user(username="test", password="testing")
        self.client.login(username="test", password="testing")

    def test_year_assignment(self):
        test_cases = create_tax_year_data_list(SINGLE_SCHEDULE_J_TEST_CASE, user=self.test_user, save=True)

        for case in test_cases:
            config = ScheduleJConfig(show_full_sch_j_form=True)
            unsorted_years_list = case["dataset_instance"].tax_years.all()
            sorted_years_list = sort_tax_years_list(unsorted_years_list)

            sch_j_instance = ScheduleJCalculation(sorted_years_list, Decimal(1000), Decimal(0), config)
            tax_for_each_year = sch_j_instance._calculate_tax_on_all_years()
            sch_j_instance._fill_form_with_tax_results(tax_for_each_year)

            sch_j_form = sch_j_instance.sch_j.to_dict()

            # Filter out null values from actual output
            filtered_form = {k: v for k, v in sch_j_form.items() if v is not None}

            assert filtered_form == case["outputs"], "Form did not match expected output"

class ScheduleJYearlyAdjustedTaxAssignmentTest(TestCase):
    def setUp(self):
        self.test_user = create_test_user(username="test", password="testing")
        self.client.login(username="test", password="testing")

    def test_year_assignment(self):
        test_cases = create_tax_year_data_list(SINGLE_SCHEDULE_J_TEST_CASE_ADJ, user=self.test_user, save=True)

        for case in test_cases:
            config = ScheduleJConfig(show_full_sch_j_form=True)
            unsorted_years_list = case["dataset_instance"].tax_years.all()
            sorted_years_list = sort_tax_years_list(unsorted_years_list)

            sch_j_instance = ScheduleJCalculation(sorted_years_list, Decimal(3000), Decimal(0), config)
            sch_j_instance._adjust_taxable_income_by_elected()
            adj_tax_for_each_year = sch_j_instance._calculate_tax_on_all_years()
            sch_j_instance._fill_form_with_adj_tax_results(adj_tax_for_each_year)

            sch_j_form = sch_j_instance.sch_j.to_dict()

            filtered_form = {k: int(v) for k, v in sch_j_form.items() if v is not None}
            assert filtered_form == case["outputs"], "Form did not match expected output"

class ScheduleJOptimizationIncomeProportionTest(TestCase):
    def setUp(self):
        self.test_user = create_test_user(username="test", password="testing")
        self.client.login(username="test", password="testing")

    def test_proportions(self):
        test_years = create_tax_year_data_list(SCHEDULE_J_OPTIMIZATION_TEST, user=self.test_user, save=True)
        for test_set in test_years:
            dataset = test_set["dataset_instance"]
            dataset.save()

            unsorted_years_list = dataset.tax_years.all()
            sorted_years = sort_tax_years_list(unsorted_years_list)
            election_year = sorted_years[0]

            calc_instance = ScheduleJOptimizer(
                tax_years=sorted_years,
                max_elected_farm_income=election_year.elected_farm_income,
                qualified_farm_income=election_year.qualified_farm_income,
                config=None)

            ordinary_percentage, qualified_percentage = calc_instance._calculate_income_proportions()
            self.assertEqual(ordinary_percentage, 1)

# @unittest.skip("Hold until optimization is refactored")
class ScheduleJOptimizationTest(TestCase):
    def setUp(self):
        self.test_user = create_test_user(username="test", password="testing")
        self.client.login(username="test", password="testing")

    def test_optimization(self):
        test_years = create_tax_year_data_list(SCHEDULE_J_OPTIMIZATION_TEST, user=self.test_user, save=True)

        for test_set in test_years:
            # Get the dataset instance
            dataset = test_set["dataset_instance"]
            dataset.save()

            unsorted_years_list = dataset.tax_years.all()
            sorted_years = sort_tax_years_list(unsorted_years_list)
            election_year = sorted_years[0]

            optimize = ScheduleJOptimizer(years=sorted_years,
                                             max_elected_farm_income=election_year.elected_farm_income,
                                             qualified_farm_income=election_year.qualified_farm_income,
                                             config=None)
            results = optimize.run_optimization()
            print(results)

CREDENTIALS = [
            ("test1", "testing123"),
            ("test2", "testing321"),
            ("test3", "testing213"),
        ]

TEST_CASES_BASIC_TAX_CALC = [
    {
        "inputs": [
            [2024, "single", 100000, 140000, False, 0, 0], # Edge case: negative ordinary income 15%
            [2023, "single", 640000, 600000, False, 0, 0], # cap gains in 0%, 15%, 20%
            [2022, "single", 640000, 540000, False, 0, 0], # Cap gains in 15%, 20%
            [2021, "single", 600000, 640000, False, 0, 0], # Edge case: negative ordinary income in 0%, 15%, 20%
        ],
        "outputs": [7946, 101271, 107848, 91647],
    },
    {
        "inputs": [
            [2024, "MFJ", 120000, 105000, False, 0, 0],
            [2023, "MFJ", 85000, 70000, False, 0, 0],
            [2022, "single", 55000, 40000, False, 0, 0],
            [2021, "MFJ", 96000, 45000, False, 0, 0],
        ],
        "outputs": [5392, 1500, 3593, 8002],
    },
    {
        "inputs": [
            [2024, "single", 230000, 200000, False, 0, 0],
            [2023, "single", 340000, 40000, False, 0, 0],
            [2022, "MFJ", 460000, 280000, False, 0, 0],
            [2021, "MFJ", 315000, 2000, False, 0, 0],
        ],
        "outputs": [30814, 82894, 72871, 63462],
    },
]

TEST_CASES_BASIC_TAX_CALC_OLDER_YEARS = [
    {
        "inputs": [
            [2021, "MFJ", 100000, 40000, False, 0, 0],
            [2020, "MFJ", 100000, 40000, False, 0, 0],
            [2019, "MFJ", 100000, 40000, False, 0, 0],
            [2018, "MFJ", 100000, 40000, False, 0, 0],
        ],
        "outputs": [9682, 9805, 9999, 10239],
    },
]

TEST_CASES_UNORGANIZED_YEARS = [
    {
        "inputs": [
            [2024, "single", 100000, 140000, False, 0, 0], # Edge case: negative ordinary income 15%
            [2023, "single", 640000, 600000, False, 0, 0], # cap gains in 0%, 15%, 20%
            [2022, "single", 640000, 540000, False, 0, 0], # Cap gains in 15%, 20%
            [2021, "single", 600000, 640000, False, 0, 0], # Edge case: negative ordinary income in 0%, 15%, 20%
        ],
        "outputs": [2024, 2023, 2022, 2021],
    },
    {
        "inputs": [
            [2023, "MFJ", 120000, 105000, False, 0, 0],
            [2024, "MFJ", 85000, 70000, False, 0, 0],
            [2021, "single", 55000, 40000, False, 0, 0],
            [2022, "MFJ", 96000, 45000, False, 0, 0],
        ],
        "outputs": [2024, 2023, 2022, 2021],
    },
    {
        "inputs": [
            [2018, "single", 230000, 200000, False, 0, 0],
            [2021, "single", 340000, 40000, False, 0, 0],
            [2019, "MFJ", 460000, 280000, False, 0, 0],
            [2020, "MFJ", 315000, 2000, False, 0, 0],
        ],
        "outputs": [2021, 2020, 2019, 2018],
    },
]

TEST_CASES_FOR_FIRST_YEAR_MAP = [
    {
        "inputs": [
            [2024, "single", 100000, 140000, False, 0, 0], # Edge case: negative ordinary income 15%
            [2023, "single", 640000, 600000, False, 0, 0], # cap gains in 0%, 15%, 20%
            [2022, "single", 640000, 540000, False, 0, 0], # Cap gains in 15%, 20%
            [2021, "single", 600000, 640000, False, 0, 0], # Edge case: negative ordinary income in 0%, 15%, 20%
        ],
        "outputs": 2024,
    },
    {
        "inputs": [
            [2023, "MFJ", 120000, 105000, False, 0, 0],
            [2024, "MFJ", 85000, 70000, False, 0, 0],
            [2021, "single", 55000, 40000, False, 0, 0],
            [2022, "MFJ", 96000, 45000, False, 0, 0],
        ],
        "outputs": 2024,
    },
    {
        "inputs": [
            [2018, "single", 230000, 200000, False, 0, 0],
            [2021, "single", 340000, 40000, False, 0, 0],
            [2019, "MFJ", 460000, 280000, False, 0, 0],
            [2020, "MFJ", 315000, 2000, False, 0, 0],
        ],
        "outputs": 2021,
    },
]

SCHEDULE_J_TEST_CASES = [
    {
        "inputs": [
            [2024, "MFJ", 107664, 10892],
            [2023, "MFJ", 126329, 9538],
            [2022, "MFJ", 129793, 4013],
            [2021, "MFJ", 226310, 203537],
        ],
        "outputs": [143, 2812, 5683, 10092],
        "elected": [13624, 0],
    },
]

BRACKET_THRESHOLDS_TEST_CASES = [
    {
        'inputs': [
            dict(year=2024, filing_status="MFJ", taxable_income=120000, qualified_income=15000, is_electing=True, elected_farm_income=10000, qualified_farm_income=0),
            dict(year=2023, filing_status="MFJ", taxable_income=85000, qualified_income=10000, is_electing=True, elected_farm_income=20000, qualified_farm_income=1000),
            dict(year=2022, filing_status="single", taxable_income=55000, qualified_income=4000, is_electing=True, elected_farm_income=5000, qualified_farm_income=0),
            dict(year=2021, filing_status="MFJ", taxable_income=496000, qualified_income=45000, is_electing=False, elected_farm_income=0, qualified_farm_income=0),
        ],
        'dataset': dict(name='Allocation Test Case 1', max_elected_farm_income=10000, qualified_farm_income=0),
        # 1 bracket below, 1 bracket above
        'results': {
            '2024': ['0.12', '0.22', '0.24'],
            '2023': ['0.10', '0.12', '0.22'],
            '2022': ['0.12', '0.22', '0.24'],
            '2021': ['0.32', '0.35', '0.37']
        }
    },
    {
        'inputs': [
                dict(year=2023, filing_status="MFJ", taxable_income=120000, qualified_income=1000, is_electing=True, elected_farm_income=10000, qualified_farm_income=0),
                dict(year=2022, filing_status="MFJ", taxable_income=185000, qualified_income=5000, is_electing=True, elected_farm_income=20000, qualified_farm_income=1000),
                dict(year=2021, filing_status="single", taxable_income=355000, qualified_income=40000, is_electing=True, elected_farm_income=5000, qualified_farm_income=0),
                dict(year=2020, filing_status="MFJ", taxable_income=96000, qualified_income=5000, is_electing=False, elected_farm_income=0, qualified_farm_income=0),
                ],
        'dataset': dict(name='Allocation Test Case 2', max_elected_farm_income=10000, qualified_farm_income=0),
        'results': {
            # 1 bracket below, 1 bracket above
            '2023': ['0.12', '0.22', '0.24'],
            '2022': ['0.12', '0.22', '0.24'],
            '2021': ['0.32', '0.35', '0.37'],
            '2020': ['0.12', '0.22', '0.24']
        }
    }
]

SCHEDULE_J_OPTIMIZATION_TEST = [
    {
        "inputs": [
            dict(year=2024, filing_status="MFJ", taxable_income=110000, qualified_income=0, is_electing=True, elected_farm_income=50000, qualified_farm_income=0),
            dict(year=2023, filing_status="MFJ", taxable_income=70000, qualified_income=0, is_electing=True, elected_farm_income=5000, qualified_farm_income=0),
            dict(year=2022, filing_status="MFJ", taxable_income=65000, qualified_income=0, is_electing=True, elected_farm_income=5000, qualified_farm_income=0),
            dict(year=2021, filing_status="MFJ", taxable_income=72000, qualified_income=0, is_electing=True, elected_farm_income=5000, qualified_farm_income=0),
        ],
        "outputs": [143, 2812, 5683, 10092],
        "dataset": {"name": "Allocation Test Case 1", "max_elected_farm_income": 50000, "qualified_farm_income": 0, "election_year": "2024"},
    },
    {
        "inputs": [
                dict(year=2022, filing_status="MFJ", taxable_income=110000, qualified_income=0, is_electing=True, elected_farm_income=50000, qualified_farm_income=25000),
                dict(year=2021, filing_status="MFJ", taxable_income=70000, qualified_income=0, is_electing=True, elected_farm_income=5000, qualified_farm_income=0),
                dict(year=2020, filing_status="MFJ", taxable_income=65000, qualified_income=0, is_electing=True, elected_farm_income=5000, qualified_farm_income=0),
                dict(year=2019, filing_status="MFJ", taxable_income=72000, qualified_income=0, is_electing=True, elected_farm_income=5000, qualified_farm_income=0),
            ],
            "outputs": [143, 2812, 5683, 10092],
            "dataset": {"name": "Allocation Test Case 1", "max_elected_farm_income": 50000, "qualified_farm_income": 0, "election_year": "2024"},
    },
]

SCHEDULE_J_INCOME_ALLOCATION_TEST = [.  
    {
        "inputs": [
            [2024, "single", 100000, 140000, True, 12000, 3000],
            [2023, "single", 640000, 600000, False, 0, 0],
            [2022, "single", 640000, 540000, False, 0, 0],
            [2021, "single", 600000, 640000, True, 15000, 0],
        ],
        "outputs": [(88000, 137000), (644000, 601000), (644000, 541000), (589000, 641000)],
    },
    {
        "inputs": [
            [2024, "MFJ", 120000, 105000, True, 60000, 0],
            [2023, "MFJ", 85000, 70000, True, 30000, 0],
            [2022, "single", 55000, 40000, False, 0, 0],
            [2021, "MFJ", 96000, 45000, False, 0, 0],
        ],
        "outputs": [(60000, 105000), (75000, 70000), (85000, 40000), (126000, 45000)],
    },
    {
        "inputs": [
            [2024, "single", 230000, 200000, True, 60000, 0],
            [2023, "single", 340000, 40000, True, 30000, 0],
            [2022, "MFJ", 460000, 280000, True, 15000, 0],
            [2021, "MFJ", 315000, 2000, True, 90000, 0],
        ],
        "outputs": [(170000, 200000), (330000, 40000), (475000, 280000), (260000, 2000)],
    },
]

FULL_SCHEDULE_J_CASES = [
    {
        "inputs": [
            {"year": 2024, "filing_status": "MFJ", "taxable_income": 120000, "qualified_income": 105000, "is_electing": True, "elected_farm_income": 10000, "qualified_farm_income": 0},
            {"year": 2023, "filing_status": "MFJ", "taxable_income": 85000, "qualified_income": 70000, "is_electing": True, "elected_farm_income": 20000, "qualified_farm_income": 1000},
            {"year": 2022, "filing_status": "single", "taxable_income": 55000, "qualified_income": 40000, "is_electing": True, "elected_farm_income": 5000, "qualified_farm_income": 0},
            {"year": 2021, "filing_status": "MFJ", "taxable_income": 96000, "qualified_income": 45000, "is_electing": False, "elected_farm_income": 0, "qualified_farm_income": 0},
        ],
        "outputs": {
            "line_1": 120000,
            "line_2a": 10000,
            "line_2b": 0.00,
            "line_3": 110000,
            "line_4": 2892,
            "line_5": 104333,
            "line_6": 3333,
            "line_7": 107667,
            "line_8": 11112,
            "line_9": 56667,
            "line_10": 3333,
            "line_11": 60000,
            "line_12": 4903,
            "line_13": 65000,
            "line_14": 3333,
            "line_15": 68333,
            "line_16": 0,
            "line_17": 18908,
            "line_18": 18908,
            "line_19": 10212,
            "line_20": 4003,
            "line_21": 0,
            "line_22": 14215,
            "line_23": 4692,
            "election_year_base_tax": 5392,
            "tax_delta": 700,
        },
        'dataset': dict(name='Allocation Test Case 1', max_elected_farm_income=10000, qualified_farm_income=0),
    },
    {
        "inputs": [
                dict(year=2023, filing_status="MFJ", taxable_income=120000, qualified_income=105000, is_electing=True, elected_farm_income=10000, qualified_farm_income=0),
                dict(year=2022, filing_status="MFJ", taxable_income=85000, qualified_income=70000, is_electing=True, elected_farm_income=20000, qualified_farm_income=1000),
                dict(year=2021, filing_status="single", taxable_income=55000, qualified_income=40000, is_electing=True, elected_farm_income=5000, qualified_farm_income=0),
                dict(year=2020, filing_status="MFJ", taxable_income=96000, qualified_income=45000, is_electing=False, elected_farm_income=0, qualified_farm_income=0),
                ],
            "outputs": {
                "line_1": 120000,
                "line_2a": 10000,
                "line_2b": 0.00,
                "line_3": 110000,
                "line_4": 3612,
                "line_5": 104333,
                "line_6": 3333,
                "line_7": 107667,
                "line_8": 11235,
                "line_9": 56667,
                "line_10": 3333,
                "line_11": 60000,
                "line_12": 5101,
                "line_13": 65000,
                "line_14": 3333,
                "line_15": 68333,
                "line_16": 0.00,
                "line_17": 19948,
                "line_18": 19948,
                "line_19": 10335,
                "line_20": 4201,
                "line_21": 0,
                "line_22": 14536,
                "line_23": 5412,
                "election_year_base_tax": 6112,
                "tax_delta": 700,
            },
            "dataset": dict(name='Allocation Test Case 1', max_elected_farm_income=10000, qualified_farm_income=0),
    }
]

SINGLE_SCHEDULE_J_TEST_CASE = [
    {
        "inputs": [
            [2024, "single", 100000, 0, False, 0, 0],
            [2023, "single", 200000, 0, False, 0, 0],
            [2022, "single", 300000, 0, False, 0, 0],
            [2021, "single", 400000, 0, False, 0, 0],
        ],
        "outputs": {"line_11": Decimal("300000.00"),
                    "line_12": Decimal("78752.65000000000000000000000"),
                    "line_15": Decimal("200000.00"),
                    "line_16": Decimal("42831.68000000000000000000000"),
                    "line_3": Decimal("100000.00"),
                    "line_4": Decimal("17052.78000000000000000000000"),
                    "line_7": Decimal("400000.00"),
                    "line_8": Decimal("114543.9000000000000000000000")},
    },
]

SINGLE_SCHEDULE_J_TEST_CASE_ADJ = [
    {
        "inputs": [
            [2024, "single", 97000, 0, False, 0, 0], # Taxable income is adjusted to account for income being allocated
            [2023, "single", 201000, 0, False, 0, 0],
            [2022, "single", 301000, 0, False, 0, 0],
            [2021, "single", 401000, 0, False, 0, 0],
        ],
        "outputs": {"line_1": 100000,
                    "line_13": 200000,
                    "line_19": 114543,
                    "line_20": 78752,
                    "line_21": 42831,
                    "line_5": 400000,
                    "line_9": 300000,
                    "election_year_base_tax": 17052},
    },
]

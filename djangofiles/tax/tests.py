from decimal import Decimal

from django.test import TestCase
from rest_framework.test import APITestCase

from .models import TaxDataSet, TaxYearData, User
from .serializers import OutputSerializer
from .services import (
    ScheduleJCalculation,
    ScheduleJOptimization,
    TaxCalculation,
    allocate_all_years,
    find_bracket_thresholds,
)
from .utils import sort_tax_years_list, update_calculations


# HELPER FUNCTIONS
def create_taxdataset(user, elected, elected_qualified):
    return TaxDataSet.objects.create(user=user, max_elected_farm_income=elected, qualified_farm_income=elected_qualified)

def create_taxyeardata(year, filing_status, taxable_income, qualified_income, dataset):
    return TaxYearData.objects.create(year=year, filing_status=filing_status, taxable_income=taxable_income,
                                  qualified_income=qualified_income, dataset=dataset)

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
        """
        If user cannot be created, an error code is displayed
        """
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
        self.test_user = create_test_user(username="test", password="testing")  # noqa: S106
        self.client.login(username="test", password="testing")  # noqa: S106

    def test_calculation(self):
        for i, test in enumerate(TEST_CASES):
            dataset = create_dataset_with_tax_years(self.test_user, test["inputs"], 0, 0)
            total_tax_results = []

            for tax_year in TaxYearData.objects.filter(dataset=dataset):
                try:
                    tax_results = TaxCalculation(tax_year).calculate_total_tax()
                    print(tax_results.upper_ordinary_bound)
                except TypeError as e:
                    print(f"❌ Test {i}: Incorrect input type - {e}")
                    tax_results = None
                except ValueError as e:
                    print(f"❌ Test {i}: Invalid input value - {e}")
                    tax_results = None

                total_tax_results.append(tax_results)

            for j, (result, expected) in enumerate(zip(total_tax_results, test["outputs"], strict=True)):
                if round(result.total_tax) != expected:
                    print(f"❌ Test {i}, Year {j}: Got {result.total_tax}, expected {expected}")

class CalculationsTest(TestCase):
    """Run base TaxCalculation to test 2021-2018. Results should match TEST outputs."""

    def setUp(self):
        self.test_user = create_test_user(username="test", password="testing")
        self.client.login(username="test", password="testing")

    def test_base_tax_calculations(self):
        # Create test sets
        for i, test in enumerate(TEST_OLDER_YEARS):
            dataset = create_dataset_with_tax_years(self.test_user, test["inputs"], 0, 0)

            total_tax_results = []
            # Base calculations
            for tax_year in TaxYearData.objects.filter(dataset=dataset):
                TaxCalculation(tax_year).calculate()
                total_tax_results.append(round(tax_year.total_tax))

            # Compare to expected
            for j, (result, expected) in enumerate(zip(total_tax_results, test["outputs"], strict=False)):
                if round(result) != expected:
                    print(f"❌ Test {i}, Year {j}: Got {result}, expected {expected}")

class ScheduleJCalculationTest(TestCase):
    """Runs Schedule J calculation in full. Compare ScheduleJForm to outputs in SCHEDULE_J_ALLOCATION_TEST."""

    def setUp(self):
        self.test_user = create_test_user(username="test", password="testing")
        self.client.login(username="test", password="testing")

    def test_serializer_outputs(self):
        test_years = create_tax_year_data_list(SCHEDULE_J_ALLOCATION_TEST, user=self.test_user, save=True)

        for test_set in test_years:
            # Get the dataset instance
            dataset = test_set["dataset_instance"]
            dataset.save()

            # Convert queryset to a list
            years = list(TaxYearData.objects.filter(dataset=dataset).order_by("-year"))

            # Base Calculations
            for year in years:
                TaxCalculation(year).calculate_total_tax()

            results_container = ScheduleJCalculation(years, dataset.max_elected_farm_income, dataset.qualified_farm_income).schedule_j_calculation()
            results = results_container.schedule_j_form.to_dict()
            correct = test_set["outputs"]

            for key in set(results.keys()).union(correct.keys()):
                val1 = results.get(key, "<missing>")
                val2 = correct.get(key, "<missing>")
                if isinstance(val1, Decimal):
                    val1 = round(float(val1), 0)

                if val1 != val2:
                    print(f"Mismatch on key '{key}': calcualtions returned {val1}, correct is {val2}")

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

            # Convert queryset to a list
            years = list(TaxYearData.objects.filter(dataset=dataset).order_by("-year"))

            # Base Calculations
            for year in years:
                TaxCalculation(year).calculate_total_tax()
            optimize = ScheduleJOptimization(years=years, elected_farm_income=dataset.max_elected_farm_income, elected_farm_qualified=dataset.qualified_farm_income, long_form=False)
            results = optimize.optimize_sch_j(elected_farm_income=dataset.max_elected_farm_income, elected_farm_qualified=dataset.qualified_farm_income)
            print(results[0].taxable_ordinary_all_years)

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

class ElectedIncomeDistributionTest(TestCase):
    """
    Make sure elected income is being distributed properly across all years. Need to update to check outputs
    """
    def setUp(self):
        self.test_user = create_test_user(username="test", password="testing")
        self.client.login(username="test", password="testing")

    def test_serializer_outputs(self):
        test_years = create_tax_year_data_list(SCHEDULE_J_ALLOCATION_TEST, user=self.test_user, save=True)

        # Get the dataset instance
        dataset = test_years[0]['dataset_instance']
        # List instead of queryset
        years = list(TaxYearData.objects.filter(dataset=dataset).order_by("-year"))
        results = allocate_all_years(years)

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
            dataset = test_set['dataset_instance']
            dataset.save()

            # Convert queryset to a list
            years = list(TaxYearData.objects.filter(dataset=dataset).order_by("-year"))
            
            # Base Calculations
            for year in years:
                TaxCalculation(year).calculate_total_tax()

            results_container = ScheduleJCalculation(years, show_all_years=True).schedule_j_calculation(dataset.max_elected_farm_income, dataset.qualified_farm_income)
            adjusted_years = results_container.tax_years
            # Test each year to see if 1 bracket below and above are returned based on taxable ordinary
            for adjusted_year in adjusted_years.values():
                bracket_threshold_results = find_bracket_thresholds(adjusted_year.year, adjusted_year.filing_status, str(adjusted_year.ordinary_rate), str(adjusted_year.ordinary_rate))
                year = adjusted_year.year
                
                expected_rates = test_set['results'][year]
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

            for i, (result, expected) in enumerate(zip(sorted_years_list, case["outputs"], strict=False)):
                if result.year != str(expected):
                    print(result.year, expected)
                    print(f"❌ Test {i}, Year {result.year}: Got {result.year}, expected {expected}")


CREDENTIALS = [
            ('test1', 'testing123'),
            ('test2', 'testing321'),
            ('test3', 'testing213'),
        ]

TEST_CASES = [
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
            [2021, "MFJ", 96000, 45000, False, 0, 0]
        ],
        "outputs": [5392, 1500, 3593, 8002],
    },
    {
        "inputs": [
            [2024, "single", 230000, 200000, False, 0, 0],
            [2023, "single", 340000, 40000, False, 0, 0],
            [2022, "MFJ", 460000, 280000, False, 0, 0],
            [2021, "MFJ", 315000, 2000, False, 0, 0]
        ],
        "outputs": [30814, 82894, 72871, 63462],
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
            [2022, "MFJ", 96000, 45000, False, 0, 0]
        ],
        "outputs": [2024, 2023, 2022, 2021],
    },
    {
        "inputs": [
            [2018, "single", 230000, 200000, False, 0, 0],
            [2021, "single", 340000, 40000, False, 0, 0],
            [2019, "MFJ", 460000, 280000, False, 0, 0],
            [2020, "MFJ", 315000, 2000, False, 0, 0]
        ],
        "outputs": [2021, 2020, 2019, 2018],
    },
]

SCHEDULE_J_TEST_CASES = [
    {
        'inputs': [
            [2024, "MFJ", 107664, 10892],
            [2023, "MFJ", 126329, 9538],
            [2022, "MFJ", 129793, 4013],
            [2021, "MFJ", 226310, 203537],
        ],
        'outputs': [143, 2812, 5683, 10092],
        'elected': [13624, 0],
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
        'inputs': [
            dict(year=2022, filing_status="MFJ", taxable_income=110000, qualified_income=0, is_electing=True, elected_farm_income=500, qualified_farm_income=0),
            dict(year=2021, filing_status="MFJ", taxable_income=70000, qualified_income=0, is_electing=True, elected_farm_income=5000, qualified_farm_income=0),
            dict(year=2020, filing_status="MFJ", taxable_income=65000, qualified_income=0, is_electing=True, elected_farm_income=5000, qualified_farm_income=0),
            dict(year=2019, filing_status="MFJ", taxable_income=72000, qualified_income=0, is_electing=True, elected_farm_income=5000, qualified_farm_income=0),
        ],
        'outputs': [143, 2812, 5683, 10092],
        'dataset': dict(name='Allocation Test Case 1', max_elected_farm_income=500, qualified_farm_income=0, election_year='2022')
    },
]

SCHEDULE_J_ALLOCATION_TEST = [
    {
        'inputs': [
            dict(year=2024, filing_status="MFJ", taxable_income=120000, qualified_income=105000, is_electing=True, elected_farm_income=10000, qualified_farm_income=0),
            dict(year=2023, filing_status="MFJ", taxable_income=85000, qualified_income=70000, is_electing=True, elected_farm_income=20000, qualified_farm_income=1000),
            dict(year=2022, filing_status="single", taxable_income=55000, qualified_income=40000, is_electing=True, elected_farm_income=5000, qualified_farm_income=0),
            dict(year=2021, filing_status="MFJ", taxable_income=96000, qualified_income=45000, is_electing=False, elected_farm_income=0, qualified_farm_income=0),
        ],
        'outputs': {
            'line_1': 120000.00,
            'line_10': 3333,
            'line_11': 60000,
            'line_12': 4903,
            'line_13': 65000,
            'line_14': 3333,
            'line_15': 68333,
            'line_16': 0.00,
            'line_17': 18908,
            'line_18': 18908,
            'line_19': 10212,
            'line_2': None,
            'line_20': 4003,
            'line_21': 0.00,
            'line_22': 14215,
            'line_23': 4692,
            'line_2a': 10000,
            'line_2b': 0,
            'line_2c': None,
            'line_3': 110000,
            'line_4': 2892,
            'line_5': 104333,
            'line_6': 3333,
            'line_7': 107667,
            'line_8': 11112,
            'line_9': 56667,
        },
        'dataset': dict(name='Allocation Test Case 1', max_elected_farm_income=10000, qualified_farm_income=0)
    },
    {
        'inputs': [
                dict(year=2023, filing_status="MFJ", taxable_income=120000, qualified_income=105000, is_electing=True, elected_farm_income=10000, qualified_farm_income=0),
                dict(year=2022, filing_status="MFJ", taxable_income=85000, qualified_income=70000, is_electing=True, elected_farm_income=20000, qualified_farm_income=1000),
                dict(year=2021, filing_status="single", taxable_income=55000, qualified_income=40000, is_electing=True, elected_farm_income=5000, qualified_farm_income=0),
                dict(year=2020, filing_status="MFJ", taxable_income=96000, qualified_income=45000, is_electing=False, elected_farm_income=0, qualified_farm_income=0),
                ],
            'outputs': {
                'line_1': 120000,
                'line_10': 3333,
                'line_11': 60000,
                'line_12': 5101,
                'line_13': 65000,
                'line_14': 3333,
                'line_15': 68333,
                'line_16': 0.00,
                'line_17': 19948,
                'line_18': 19948,
                'line_19': 10335,
                'line_2': None,
                'line_20': 4201,
                'line_21': 0,
                'line_22': 14536,
                'line_23': 5412,
                'line_2a': 10000,
                'line_2b': 0.00,
                'line_2c': None,
                'line_3': 110000,
                'line_4': 3612,
                'line_5': 104333,
                'line_6': 3333,
                'line_7': 107667,
                'line_8': 11235,
                'line_9': 56667,
            },
            'dataset': dict(name='Allocation Test Case 1', max_elected_farm_income=10000, qualified_farm_income=0)
    }
]

TEST_OLDER_YEARS = [
    {
        'inputs': [
            [2021, "MFJ", 100000, 40000, False, 0, 0],
            [2020, "MFJ", 100000, 40000, False, 0, 0],
            [2019, "MFJ", 100000, 40000, False, 0, 0],
            [2018, "MFJ", 100000, 40000, False, 0, 0],
        ],
        'outputs': [9682, 9805, 9999, 10239],
    },
]
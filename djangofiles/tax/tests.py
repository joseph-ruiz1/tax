from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth import get_user_model


from .models import TaxYearData, TaxDataSet, User, CalculationIteration, AdjustedTaxData, ScheduleJForm
from .utils import build_taxyear_formset_data, chunker
from .services import TaxCalculation, ScheduleJCalculation, ScheduleJOptimization

def create_taxdataset(user, elected, elected_qualified):
    return TaxDataSet.objects.create(user=user, max_elected_farm_income=elected, qualified_farm_income=elected_qualified)


def create_taxyeardata(year, filing_status, taxable_income, qualified_income, dataset):
    return TaxYearData.objects.create(year=year, filing_status=filing_status, taxable_income=taxable_income, \
                                  qualified_income=qualified_income, dataset=dataset)

def create_dataset_with_tax_years(user, tax_year_inputs: tuple, elected, elected_qualified):
    dataset = create_taxdataset(user, elected, elected_qualified)
    for tax_year in tax_year_inputs:
        year, filing_status, taxable_income, qualified_income = tax_year

        TaxYearData.objects.create(
            dataset=dataset,
            year=year,
            filing_status=filing_status,
            taxable_income=taxable_income,
            qualified_income=qualified_income
        )
    return dataset

def create_test_user(username, password):
    return User.objects.create_user(username=username, password=password)

def create_several_test_users(username, password):
    return User.objects.create_user(username=username, password=password)



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
        """
        
        """
        
        users = [create_several_test_users(username, password) for username, password in CREDENTIALS]

        self.assertEqual(User.objects.count(), len(CREDENTIALS))

        expected_ids = list(range(1, len(users) + 1))
        actual_ids = [user.id for user in users]
        self.assertEqual(actual_ids, expected_ids)




class TaxDataSetModelTest(TestCase):
    """
    Testing the InputsCreateView and validates a few tax calcs
    """
    def setUp(self):
        self.test_user = create_test_user(username="test", password="testing")
        self.client.login(username="test", password="testing")
                        
    def test_load_single_set_with_years(self):
        """
        Loads a single TaxDataSet instance into the view from dashboard and checks that all years are input properly
        """
        response = self.client.get(reverse("tax:start-dataset"))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse("tax:start-dataset"), data={"name": "test", "max_elected_farm_income": 10000, "qualified_farm_income": 1000}, follow=True)
        self.assertEqual(TaxDataSet.objects.filter(user=self.test_user).count(), 1)
        self.assertEqual(response.status_code, 200)

        # Redirect
        dataset = TaxDataSet.objects.filter(user=self.test_user).latest("id")
        input_url = reverse("tax:inputs", kwargs={"dataset_pk": dataset.pk})

        tax_data_inputs = [
            (2024, "single", 100000, 40000,),
            (2023, "MFJ", 20000, 100,),
            (2022, "MFJ", 2000, 50,),
            (2021, "single", 100000, 10000,),
        ]
        
        formset_data = build_taxyear_formset_data(tax_data_inputs)

        response = self.client.post(input_url, formset_data, follow=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(TaxDataSet.objects.filter(user=self.test_user).count(), 1, "uhhh")
        self.assertEqual(TaxYearData.objects.filter(dataset__user=self.test_user).count(), 4, "Not saved to DB")
        self.assertEqual(TaxYearData.objects.filter(dataset__user=self.test_user).first().year, "2024")
        


    def test_load_multiple_sets_check_base_calculations(self):
        """
        Validates that all base year calculations are correct
        """
        # Create first set and POST initial data
        response = self.client.get(reverse("tax:start-dataset"))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse("tax:start-dataset"), data={"name": "test", "max_elected_farm_income": 10000, "qualified_farm_income": 1000}, follow=True)
        self.assertEqual(TaxDataSet.objects.filter(user=self.test_user).count(), 1)
        self.assertEqual(response.status_code, 200)

        # Redirect
        dataset = TaxDataSet.objects.filter(user=self.test_user).latest("id")
        input_url = reverse("tax:inputs", kwargs={"dataset_pk": dataset.pk})

        # Formset we want to POST
        tax_data_inputs = [
            (2024, "single", 100000, 40000,),
            (2023, "MFJ", 20000, 100,),
            (2022, "MFJ", 2000, 50,),
            (2021, "single", 100000, 10000,),
        ]
        
        formset_data = build_taxyear_formset_data(tax_data_inputs)
        # POST that formset
        response = self.client.post(input_url, formset_data, follow=True)
        self.assertEqual(response.status_code, 200)
        

        # Create Second Set
        response = self.client.get(reverse("tax:start-dataset"))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse("tax:start-dataset"), data={"name": "test2", "max_elected_farm_income": 5000, "qualified_farm_income": 40}, follow=True)
        self.assertEqual(TaxDataSet.objects.filter(user=self.test_user).count(), 2)
        self.assertEqual(response.status_code, 200)

        # Redirect
        dataset = TaxDataSet.objects.filter(user=self.test_user).latest("id")
        input_url = reverse("tax:inputs", kwargs={"dataset_pk": dataset.pk})

        tax_data_inputs = [
            (2024, "MFJ", 120000, 105000,),
            (2023, "MFJ", 85000, 70000,),
            (2022, "single", 55000, 40000,),
            (2021, "MFJ", 96000, 45000,)
        ]

        formset_data = build_taxyear_formset_data(tax_data_inputs)
        response = self.client.post(input_url, formset_data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(TaxYearData.objects.filter(dataset__pk=dataset.pk).count(), 4, "Second set of years not saved to DB")
        self.assertEqual(TaxDataSet.objects.filter(user=self.test_user).count(), 2, "Sets not saved to DB")
        self.assertEqual(TaxYearData.objects.filter(dataset__user=self.test_user).count(), 8, "All TaxYearDatas not saved to DB")


class BaseTaxCalculationsTest(TestCase):
    def setUp(self):
        self.test_user = create_test_user(username="test", password="testing")
        self.client.login(username="test", password="testing")

    def test_base_tax_calculations(self):
        # Create test sets
        for i, test in enumerate(TEST_CASES):
            dataset = create_dataset_with_tax_years(self.test_user, test['inputs'], 0, 0)

            total_tax_results = []
            # Base calculations
            for tax_year in TaxYearData.objects.filter(dataset=dataset):
                TaxCalculation(tax_year).calculate()
                total_tax_results.append(round(tax_year.total_tax))

            # Compare to expected
            for j, (result, expected) in enumerate(zip(total_tax_results, test['outputs'])):
                if round(result) != expected:
                    print(f"❌ Test {i}, Year {j}: Got {result}, expected {expected}")


class ScheduleJCalculationsTest(TestCase):
    def setUp(self):
        self.test_user = create_test_user(username="test", password="testing")
        self.client.login(username="test", password="testing")

    def test_sch_j_calculations(self):
            for i, test in enumerate(SCHEDULE_J_TEST_CASES):
                max_elected, qualified_elected = test["elected"]
                dataset = create_dataset_with_tax_years(self.test_user, test['inputs'], max_elected, qualified_elected)
                dataset.refresh_from_db()

                # Base Calculations
                for tax_year in TaxYearData.objects.filter(dataset=dataset):
                    TaxCalculation(tax_year).calculate()

                sch_j_results = []
                #Schedule J calculation
                tax_years = TaxYearData.objects.filter(dataset=dataset).order_by("-year")
                i = CalculationIteration.objects.create(dataset=dataset)
                ScheduleJCalculation(*tax_years, i).schedule_j_calculation(dataset.max_elected_farm_income, dataset.qualified_farm_income)
                

                for adjusted in AdjustedTaxData.objects.filter(iteration=i).order_by("-year"):
                    sch_j_results.append(adjusted)

                for j, (result, expected) in enumerate(zip(sch_j_results, test['outputs'])):
                    if round(result.total_tax) != expected:
                        print(f"❌ Test {i}, Year {j}: Got {result.total_tax}, expected {expected}")
                        print(f"ordinary: {result.ordinary_tax}, qualified: {result.qualified_tax}")


class ScheduleJOptimizationTest(TestCase):
    def setUp(self):
        self.test_user = create_test_user(username="test", password="testing")
        self.client.login(username="test", password="testing")

    def test_optimization(self):
        for i, test in enumerate(SCHEDULE_J_OPT_TEST):
                max_elected, max_qualified_elected = test["elected"]
                dataset = create_dataset_with_tax_years(self.test_user, test['inputs'], max_elected, max_qualified_elected)
                dataset.refresh_from_db()

                years = TaxYearData.objects.filter(dataset=dataset).order_by("-year")

                # Base Calculations
                for year in years:
                    TaxCalculation(year).calculate()

        optimize = ScheduleJOptimization(*years, elected_farm_income=dataset.max_elected_farm_income, elected_farm_qualified=dataset.qualified_farm_income, dataset=dataset)
        optimize.optimize_sch_j(dataset.max_elected_farm_income, dataset.qualified_farm_income)
        
        results = ScheduleJForm.objects.filter(iteration__dataset=dataset).values_list("line_23", flat=True)
        print(dataset.return_optimal_amount())
        

           
CREDENTIALS = [
            ('test1', 'testing123'), 
            ('test2', 'testing321'), 
            ('test3', 'testing213'),
        ]

TEST_CASES = [
    {
        'inputs': [
            [2024, "single", 100000, 40000],
            [2023, "MFJ", 20000, 100],
            [2022, "MFJ", 2000, 50],
            [2021, "single", 100000, 10000],
        ],
        'outputs': [14253, 1990, 195, 17121],
    },
    {
        'inputs': [
            [2024, "MFJ", 120000, 105000],
            [2023, "MFJ", 85000, 70000],
            [2022, "single", 55000, 40000],
            [2021, "MFJ", 96000, 45000]
        ],
        'outputs': [5392, 1500, 3593, 8002],
    },
    {
        'inputs': [
            [2024, "single", 230000, 200000],
            [2023, "single", 340000, 40000],
            [2022, "MFJ", 460000, 280000],
            [2021, "MFJ", 315000, 2000]
        ],
        'outputs': [30814, 82894, 72871, 63462],
    },
]


SCHEDULE_J_TEST_CASES = [
    {
        'inputs': [
            [2024, "MFJ", 120000, 105000],
            [2023, "MFJ", 85000, 70000],
            [2022, "single", 55000, 40000],
            [2021, "MFJ", 96000, 45000],
        ],
        'outputs': [143, 2812, 5683, 10092],
        'elected': [25000, 4000],
    },
    {
        'inputs': [
            [2024, "single", 230000, 200000],
            [2023, "single", 340000, 40000],
            [2022, "MFJ", 460000, 280000],
            [2021, "MFJ", 315000, 2000],
        ],
        'outputs': [23896, 85911, 74971, 65562],
        'elected': [27000, 2000]
    },
]

SCHEDULE_J_OPT_TEST = [
    {
        'inputs': [
            [2024, "MFJ", 120000, 105000],
            [2023, "MFJ", 85000, 70000],
            [2022, "single", 55000, 40000],
            [2021, "MFJ", 96000, 45000],
        ],
        'outputs': [143, 2812, 5683, 10092],
        'elected': [25000, 4000],
    },
]
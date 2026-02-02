import pytest
from rest_framework.test import APIClient
from sample_user_data import SAMPLE_USER_DATA, SAMPLE_USER_DATA_NO_CONFIRMATION
from tax.models import TaxDataSet, TaxYearData, User


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()

@pytest.fixture
def test_user(db):
    return User.objects.create_user(**SAMPLE_USER_DATA_NO_CONFIRMATION["user_1"])

@pytest.fixture
def test_user_2(db):
    return User.objects.create_user(**SAMPLE_USER_DATA_NO_CONFIRMATION["user_2"])

@pytest.fixture
def authenticated_client(api_client, test_user):
    api_client.force_authenticate(user=test_user)
    return api_client

@pytest.fixture
def authenticated_client_2(api_client, test_user_2):
    api_client.force_authenticate(user=test_user_2)
    return api_client

@pytest.fixture
def create_empty_dataset():
    def _create(user, election_year: int = 2024):
        dataset = TaxDataSet.objects.create(user=user)
        for year in range(election_year - 3, election_year + 1):
            TaxYearData.objects.create(dataset=dataset, year=year)
        dataset.save()
        return dataset
    return _create

@pytest.fixture
def dataset(test_user, create_empty_dataset):
    return create_empty_dataset(user=test_user)

@pytest.fixture
def datasets(test_user, create_empty_dataset):
    return [create_empty_dataset(test_user) for _ in range(3)]

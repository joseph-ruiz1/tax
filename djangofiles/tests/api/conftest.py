import pytest
from rest_framework.test import APIClient
from sample_user_data import SAMPLE_USER_DATA, SAMPLE_USER_DATA_NO_CONFIRMATION
from tax.models import User


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()

@pytest.fixture
def authenticated_client(api_client, test_user):
    api_client.force_authenticate(user=test_user)
    return api_client

@pytest.fixture
def user(db):
    return User.objects.create_user(**SAMPLE_USER_DATA_NO_CONFIRMATION)

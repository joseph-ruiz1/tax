import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client() -> APIClient:
    yield APIClient()

@pytest.fixture
def authenticated_client(api_client, test_user):
    api_client.force_authenticate(user=test_user)
    return api_client


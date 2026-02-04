import pytest
from rest_framework import status, exceptions
from sample_user_data import (
    CREDENTIALS,
    SAMPLE_USER_DATA,
    SAMPLE_USER_DATA_NO_CONFIRMATION,
)
from tax.models import TaxDataSet, TaxYearData, User
from tax.serializers import DEFAULT_ELECTION_YEAR
from test_api_data import TAX_INPUTS
from tests.calculations.calculation_cases import BASIC_TAX_CALCULATION_INPUTS
from utils import update_inputs, add_pk_to_tax_year


@pytest.mark.django_db
class TestUserModel:
    def test_create_single_user(self):
        test_user = User.objects.create_user(username="test", password="testing123")
        assert User.objects.count() == 1
        assert test_user.username == "test"
        assert test_user.id == 1

    def test_create_several_users(self):
        users = [User.objects.create_user(username, password) for username, password in CREDENTIALS]

        assert User.objects.count() == len(CREDENTIALS)

        expected_ids = list(range(1, len(users) + 1))
        actual_ids = [user.id for user in users]
        assert actual_ids == expected_ids

class BaseAPITest:
    @staticmethod
    def assert_successful_response(response, expected_status=status.HTTP_200_OK):
        assert response.status_code == expected_status

    @staticmethod
    def assert_successful_creation(response, expected_status=status.HTTP_201_CREATED):
        assert response.status_code == expected_status

    @staticmethod
    def assert_failed_response(response, expected_status=status.HTTP_400_BAD_REQUEST):
        assert response.status_code == expected_status

    @staticmethod
    def assert_failed_creation(response, expected_status=status.HTTP_403_FORBIDDEN):
        assert response.status_code == expected_status

    @staticmethod
    def assert_field_failure(response, failed_field, failure_message, failure_number=0):
        error = response.data["errors"][failed_field][failure_number]
        if isinstance(error, exceptions.ErrorDetail):
            assert error.title() == failure_message
        if isinstance(error, dict):
            BaseAPITest.assert_validation_failure(error, failure_message, failure_number)

    @staticmethod
    # Probably buggy with the list indexes
    def assert_validation_failure(error_map, failure_message, failure_numer=0):
        # Used if error is coming from model validation
        errors = list(error_map.values())
        assert errors[failure_numer][0] == failure_message

@pytest.mark.django_db
class TestAuthViewSet(BaseAPITest):
    def test_regular_user_creation(self, api_client):
        response = api_client.post(
            "/tax/api/auth/register/",
            data=SAMPLE_USER_DATA["user_1"],
            format="json",
            follow=True)
        self.assert_successful_creation(response)

        user = User.objects.get(username=SAMPLE_USER_DATA["user_1"]["username"])

        assert user.is_authenticated

    def test_register_duplicate_username(self, api_client, test_user):
        response = api_client.post(
            "/tax/api/auth/register/",
            data=SAMPLE_USER_DATA["user_1"],
            format="json",
            follow=True,
        )
        self.assert_failed_response(response)
        self.assert_field_failure(response, "username", "A User With That Username Already Exists.")

    def test_register_no_password(self, api_client):
        response = api_client.post(
            "/tax/api/auth/register/",
            data={"username": "test"},
            format="json",
            follow=True,
        )
        self.assert_failed_response(response)
        self.assert_field_failure(response, "password", "This Field Is Required.")

    def test_register_no_confirmation(self, api_client):
        response = api_client.post(
            "/tax/api/auth/register/",
            data=SAMPLE_USER_DATA_NO_CONFIRMATION["user_1"],
            format="json",
            follow=True,
        )
        self.assert_failed_response(response)
        self.assert_field_failure(response, "password_confirm", "This Field Is Required.")


    def test_login(self, api_client, test_user):
        response = api_client.post(
            "/tax/api/auth/login/",
            data=SAMPLE_USER_DATA_NO_CONFIRMATION["user_1"],
            format="json",
            follow=True,
        )
        self.assert_successful_response(response)
        assert response.data["message"] == "Login successful"

    def test_invalid_login(self, api_client, test_user):
        response = api_client.post(
            "/tax/api/auth/login/",
            data={"username": SAMPLE_USER_DATA["user_1"]["username"], "password": "incorrect"},
            format="json",
            follow=True,
        )
        self.assert_failed_response(response)
        self.assert_field_failure(response, "non_field_errors", "Invalid Credentials")

    def test_logout(self, authenticated_client, test_user):
        response = authenticated_client.post("/tax/api/auth/logout/")
        self.assert_successful_response(response)
        assert response.data["message"] == "Logout successful"

    def test_check_auth(self, authenticated_client, test_user):
        response = authenticated_client.get("/tax/api/auth/check/")
        self.assert_successful_response(response)
        assert response.data["authenticated"] is True

    def test_check_unauthenticated(self, api_client):
        response = api_client.get("/tax/api/auth/check/")
        self.assert_successful_response(response)
        assert response.data["authenticated"] is False


class TestDataSetViewSet(BaseAPITest):
    def test_create_dataset(self, authenticated_client):
        response = authenticated_client.post(
            "/tax/api/datasets/create/",
            data={},
            format="json",
        )
        self.assert_successful_creation(response)

        dataset = TaxDataSet.objects.get(id=response.data["dataset_id"])
        assert TaxDataSet.objects.filter(id=dataset.id).exists()
        assert dataset.election_year == DEFAULT_ELECTION_YEAR

    def test_create_dataset_unauthenticated(self, api_client):
        response = api_client.post(
            "/tax/api/datasets/create/",
            data={},
            format="json",
        )
        self.assert_failed_creation(response)

    def test_list_datasets(self, authenticated_client, datasets):
        response = authenticated_client.get("/tax/api/datasets/")
        self.assert_successful_response(response)
        assert len(response.data) == len(datasets)

    def test_list_datasets_filter_by_user(self, authenticated_client, test_user_2, datasets, create_empty_dataset):
        create_empty_dataset(test_user_2)

        response = authenticated_client.get("/tax/api/datasets/")
        self.assert_successful_response(response)
        assert len(response.data) == len(datasets)

    def test_retrieve_dataset(self, authenticated_client, dataset):
        response = authenticated_client.get(f"/tax/api/datasets/{dataset.id}/")
        self.assert_successful_response(response)
        assert response.data["id"] == 1

    def test_retrieve_invalid_dataset(self, authenticated_client, test_user_2, create_empty_dataset):
        dataset = create_empty_dataset(test_user_2)
        response = authenticated_client.get(f"/tax/api/datasets/{dataset.id}/")
        # Keeping 404 error instead of 403 or 401 could be better for security, but perhaps not debugging
        # https://auth0.com/blog/forbidden-unauthorized-http-status-codes/#:~:text=Don%27t%20let%20the%20client%20know
        self.assert_failed_response(response, status.HTTP_404_NOT_FOUND)

    def test_delete_dataset(self, authenticated_client, dataset):
        response = authenticated_client.delete(f"/tax/api/datasets/{dataset.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_new_entry(self, authenticated_client, dataset):
        test_data = TAX_INPUTS["basic_scenario"]
        add_pk_to_tax_year(dataset, test_data)
        response = authenticated_client.patch(
            f"/tax/api/datasets/{dataset.id}/new/",
            data=test_data,
            format="json",
        )
        print(response.data)
        self.assert_successful_response(response)

class TestTaxEntries(BaseAPITest):
    @pytest.mark.parametrize(
        "scenario, invalid_year",
        [
            ("basic_scenario", "2026"),
            ("basic_scenario", "2017"),
        ],
    )
    def test_invalid_tax_year(self, authenticated_client, dataset_with_tax_year_pk, scenario, invalid_year):
        test_data = dataset_with_tax_year_pk(scenario)
        test_data["tax_years"][0]["year"] = invalid_year

        response = authenticated_client.patch(
            f"/tax/api/datasets/{dataset_with_tax_year_pk.id}/new/",
            data=test_data,
            format="json",
        )
        self.assert_failed_response(response)
        self.assert_field_failure(response, "tax_years", f'"{invalid_year}" is not a valid choice.')




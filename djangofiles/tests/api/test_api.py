import pytest
from django.urls import reverse
from rest_framework import exceptions, status
from sample_user_data import (
    SAMPLE_USER_DATA,
    SAMPLE_USER_DATA_NO_CONFIRMATION,
)
from tax.models import TaxDataSet, User
from tax.serializers import DEFAULT_ELECTION_YEAR


class BaseAPITest:
    @staticmethod
    def assert_field_failure(response, failed_field, failure_message, failure_number=0):
        error = response.data["errors"][failed_field][failure_number]
        if isinstance(error, exceptions.ErrorDetail):
            assert error.title() == failure_message
        if isinstance(error, dict):
            BaseAPITest.assert_validation_failure(error, failure_message, failure_number)

    @staticmethod
    def assert_auth_failure(response, failed_field, failure_code, failure_number=0):
        error = response.data[failed_field][failure_number]
        assert error.code == failure_code

    @staticmethod
    # Probably buggy with the list indexes
    def assert_validation_failure(error_map, failure_message, failure_numer=0):
        # Used if error is coming from model validation
        errors = list(error_map.values())
        assert errors[failure_numer][0] == failure_message

@pytest.mark.django_db
class TestAuth(BaseAPITest):
    def test_user_creation(self, api_client):
        response = api_client.post(
            reverse("tax:rest_register"),
            data=SAMPLE_USER_DATA["user_1"],
            format="json",
            follow=True,
        )
        assert response.status_code == status.HTTP_201_CREATED
        user = User.objects.get(username=SAMPLE_USER_DATA["user_1"]["username"])
        assert user.is_authenticated

    def test_register_duplicate_username(self, api_client, test_user):
        response = api_client.post(
            reverse("tax:rest_register"),
            data=SAMPLE_USER_DATA["user_1"],
            format="json",
            follow=True,
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        self.assert_auth_failure(response, "username", "username_taken")

    def test_register_no_password(self, api_client):
        response = api_client.post(
            reverse("tax:rest_register"),
            data={"username": "test"},
            format="json",
            follow=True,
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        self.assert_auth_failure(response, "password1", "required")

    def test_register_no_confirmation(self, api_client):
        response = api_client.post(
            reverse("tax:rest_register"),
            data=SAMPLE_USER_DATA_NO_CONFIRMATION["user_1"],
            format="json",
            follow=True,
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        self.assert_auth_failure(response, "password2", "required")

    def test_login(self, api_client, test_user):
        response = api_client.post(
            reverse("tax:rest_login"),
            data=SAMPLE_USER_DATA_NO_CONFIRMATION["user_1"],
            format="json",
            follow=True,
        )
        assert response.status_code == status.HTTP_200_OK

    def test_invalid_login(self, api_client, test_user):
        response = api_client.post(
            reverse("tax:rest_login"),
            data={"username": SAMPLE_USER_DATA["user_1"]["username"], "password": "incorrect"},
            format="json",
            follow=True,
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        self.assert_auth_failure(response, "non_field_errors", "invalid")

    def test_logout(self, authenticated_client, test_user):
        response = authenticated_client.post(reverse("tax:rest_logout"))
        assert response.status_code == status.HTTP_200_OK

    def test_check_auth(self, authenticated_client, test_user):
        response = authenticated_client.get(reverse("tax:rest_user_details"))
        assert response.status_code == status.HTTP_200_OK

    def test_check_unauthenticated(self, api_client):
        response = api_client.get(reverse("tax:rest_user_details"))
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data["detail"].code == "not_authenticated"


class TestDataSetViewSet(BaseAPITest):
    def test_create_dataset(self, authenticated_client):
        response = authenticated_client.post(
            reverse("tax:dataset-create-step"),
            data={},
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED

        dataset = TaxDataSet.objects.get(id=response.data["dataset_id"])
        assert TaxDataSet.objects.filter(id=dataset.id).exists()
        assert dataset.election_year == DEFAULT_ELECTION_YEAR

    def test_create_dataset_unauthenticated(self, api_client):
        response = api_client.post(
            reverse("tax:dataset-create-step"),
            data={},
            format="json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_datasets(self, authenticated_client, datasets):
        response = authenticated_client.get(reverse("tax:dataset-list"))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == len(datasets)

    def test_list_datasets_filter_by_user(self, authenticated_client, test_user_2, datasets, create_empty_dataset):
        create_empty_dataset(test_user_2)

        response = authenticated_client.get(reverse("tax:dataset-list"))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == len(datasets)

    def test_retrieve_dataset(self, authenticated_client, dataset):
        response = authenticated_client.get(reverse("tax:dataset-detail", kwargs={"pk": dataset.id}))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == 1

    def test_retrieve_invalid_dataset(self, authenticated_client, test_user_2, create_empty_dataset):
        dataset = create_empty_dataset(test_user_2)
        response = authenticated_client.get(reverse("tax:dataset-detail", kwargs={"pk": dataset.id}))
        # Keeping 404 error instead of 403 or 401 could be better for security, but perhaps not debugging
        # https://auth0.com/blog/forbidden-unauthorized-http-status-codes/#:~:text=Don%27t%20let%20the%20client%20know
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_dataset(self, authenticated_client, dataset):
        response = authenticated_client.delete(reverse("tax:dataset-detail", kwargs={"pk": dataset.id}))
        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.parametrize(
        "scenario",
        [("basic_scenario")],
    )
    def test_new_entry(self, authenticated_client, dataset, dataset_with_tax_year_pk, scenario):
        test_data = dataset_with_tax_year_pk(scenario)

        response = authenticated_client.patch(
            reverse("tax:dataset-new-entry", kwargs={"pk": dataset.id}),
            data=test_data,
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK

class TestTaxEntries(BaseAPITest):
    @pytest.mark.parametrize(
        "scenario, invalid_year",
        [
            ("basic_scenario", "2026"),
            ("basic_scenario", "2017"),
        ],
    )
    def test_invalid_tax_year(self, authenticated_client, dataset, dataset_with_tax_year_pk, scenario, invalid_year):
        test_data = dataset_with_tax_year_pk(scenario)
        test_data["tax_years"][0]["year"] = invalid_year

        response = authenticated_client.patch(
            reverse("tax:dataset-new-entry", kwargs={"pk": dataset.id}),
            data=test_data,
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        self.assert_field_failure(response, "tax_years", f'"{invalid_year}" is not a valid choice.')

    @pytest.mark.parametrize(
        "invalid_income, expected_msg",
        [
            (1000000000, "Ensure that there are no more than 9 digits before the decimal point."),
            (-1000, "Income must be positive"),
        ],
    )
    def test_invalid_taxable_income(self, authenticated_client, dataset, dataset_with_tax_year_pk, invalid_income, expected_msg):
        test_data = dataset_with_tax_year_pk("basic_scenario")
        test_data["tax_years"][0]["taxable_income"] = invalid_income

        response = authenticated_client.patch(
            reverse("tax:dataset-new-entry", kwargs={"pk": dataset.id}),
            data=test_data,
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        self.assert_field_failure(response, "tax_years", f"{expected_msg}")

    def test_unsorted_years(self, authenticated_client, dataset, dataset_with_tax_year_pk):
        unsorted_data = dataset_with_tax_year_pk("unsorted_older_years")
        response = authenticated_client.patch(
            reverse("tax:dataset-new-entry", kwargs={"pk": dataset.id}),
            data=unsorted_data,
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        self.assert_field_failure(response, "non_field_errors", "Years Must Be In Descending Order")

import pytest
from rest_framework import status
from sample_user_data import CREDENTIALS, SAMPLE_USER_DATA, SAMPLE_USER_DATA_NO_CONFIRMATION
from tax.models import TaxDataSet, TaxYearData, User


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
    def assert_field_failure(response, failed_field, failure_message, failure_numer=0):
        error = response.data["errors"][failed_field][failure_numer]
        assert error.title() == failure_message

@pytest.mark.django_db
def test_create_user(api_client, test_user) -> None:
    response_create = api_client.post("/tax/api/")

@pytest.mark.django_db
class TestAuthViewSet(BaseAPITest):
    def test_regular_user_creation(self, api_client):
        response = api_client.post(
            "/tax/api/auth/register/",
            data=SAMPLE_USER_DATA,
            format="json",
            follow=True)
        self.assert_successful_creation(response)

        user = User.objects.get(username=SAMPLE_USER_DATA["username"])

        assert user.is_authenticated

    def test_register_duplicate_username(self, api_client, user):
        response = api_client.post(
            "/tax/api/auth/register/",
            data=SAMPLE_USER_DATA,
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
            data=SAMPLE_USER_DATA_NO_CONFIRMATION,
            format="json",
            follow=True,
        )
        self.assert_failed_response(response)
        self.assert_field_failure(response, "password_confirm", "This Field Is Required.")


    def test_login(self, api_client, user):
        response = api_client.post(
            "/tax/api/auth/login/",
            data=SAMPLE_USER_DATA_NO_CONFIRMATION,
            format="json",
            follow=True,
        )
        self.assert_successful_response(response)
        assert response.data["message"] == "Login successful"

    def test_invalid_login(self, api_client, user):
        response = api_client.post(
            "/tax/api/auth/login/",
            data={"username": SAMPLE_USER_DATA["username"], "password": "incorrect"},
            format="json",
            follow=True,
        )
        self.assert_failed_response(response)
        self.assert_field_failure(response, "non_field_errors", "Invalid Credentials")

    def test_logout(self, authenticated_client, user):
        response = authenticated_client.post("/tax/api/auth/logout/")
        self.assert_successful_response(response)
        assert response.data["message"] == "Logout successful"

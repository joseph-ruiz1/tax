import pytest
from api.sample_user_data import CREDENTIALS
from tax.models import User


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

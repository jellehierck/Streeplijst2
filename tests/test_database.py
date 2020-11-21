import pytest
import copy

from streeplijst2.database import UserDB
import streeplijst2.api as api
from streeplijst2.config import TEST_USER, TEST_USER_NO_SDD

from datetime import datetime

# Add some extra fields to the test user
TEST_USER_1 = copy.deepcopy(TEST_USER)

# Create a duplicate object (deep copy so they do not reference the same object)
TEST_USER_DUP = copy.deepcopy(TEST_USER_1)

# Create a user with extra unnecessary fields
TEST_USER_EXTRA_FIELDS = copy.deepcopy(TEST_USER_1)
TEST_USER_EXTRA_FIELDS['email'] = 'hello@world.com'

# Create a user which has some fields which differ from the regular test user
TEST_USER_UPDATED = copy.deepcopy(TEST_USER_1)
TEST_USER_UPDATED.update(dict({
    's_number': 's9999990',
    'first_name': 'Test2',
    'last_name_prefix': 'the',
    'last_name': 'Testuser2',
    'date_of_birth': datetime.fromisocalendar(2001, 2, 2),
    'has_sdd_mandate': False,
}))

# Create a second test user and add some important fields
TEST_USER_2 = copy.deepcopy(TEST_USER_NO_SDD)


class TestUser:

    def test_create_user(self, test_app):
        with test_app.app_context():
            user = UserDB.create(**TEST_USER_1)
            for (key, value) in TEST_USER_1.items():  # Make sure all fields are stored correctly
                assert user.__getattribute__(key) == value

    def test_create_user_extra_fields(self, test_app):
        with test_app.app_context():
            user = UserDB.create(**TEST_USER_EXTRA_FIELDS)  # Create a user with fields which are not needed
            required_fields = ((key, value) for (key, value) in TEST_USER_EXTRA_FIELDS.items() if key != 'email')
            for (key, value) in required_fields:  # Make sure all fields are stored correctly
                assert user.__getattribute__(key) == value
            assert hasattr(user, 'email') is False

    def test_create_user_duplicate(self, test_app):
        with test_app.app_context():
            user = UserDB.create(**TEST_USER_1)
            duplicate_user = UserDB.create(**TEST_USER_DUP)
            assert user is duplicate_user  # Make sure the same user is referenced in case of a duplicate

    def test_get_user(self, test_app):
        with test_app.app_context():
            user = UserDB.create(**TEST_USER_1)
            other_user = UserDB.get(TEST_USER_1['id'])
            assert user is other_user  # Make sure both objects are the same instance

    def test_get_user_by_s_number(self, test_app):
        with test_app.app_context():
            user = UserDB.create(**TEST_USER_1)
            other_user = UserDB.get_by_s_number(TEST_USER_1['s_number'])
            assert user is other_user  # Make sure both objects are the same instance

    def test_update_user(self, test_app):
        with test_app.app_context():
            user = UserDB.create(**TEST_USER_1)
            updated_user = UserDB.update(**TEST_USER_UPDATED)
            for (key, value) in TEST_USER_UPDATED.items():  # Make sure all values are updated as expected
                assert updated_user.__getattribute__(key) == value
                assert user.__getattribute__(key) == updated_user.__getattribute__(key)

    def test_delete_user(self, test_app):
        with test_app.app_context():
            user = UserDB.create(**TEST_USER_1)
            get_user = UserDB.get(TEST_USER_1['id'])
            assert get_user is not None  # Make sure the user is retrieved

            deleted_user = UserDB.delete(TEST_USER_1['id'])
            assert user is deleted_user  # Make sure the same object is referenced

            get_user = UserDB.get(TEST_USER_1['id'])
            assert get_user is None  # Make sure the user is not retrieved

    def test_list_all_users(self, test_app):
        with test_app.app_context():
            user2 = UserDB.create(**TEST_USER_2)
            user1 = UserDB.create(**TEST_USER_1)
            user_list = UserDB.list_all()
            assert len(user_list) == 2  # Make sure exactly two users are returned
            assert user1 == user_list[0]  # Make sure each user is in the list
            assert user2 == user_list[1]  # Also make sure the order is correct (ascending id)


class TestUserAPI:
    """
    Integration tests between the database and api.
    """

    def test_get_user(self, test_app):
        with test_app.app_context():
            user_dict = api.get_user(TEST_USER['s_number'])
            user = UserDB.create(**user_dict)
            for (key, value) in TEST_USER.items():  # Make sure all fields are stored correctly
                assert user.__getattribute__(key) == value

    def test_get_user_duplicate(self, test_app):
        with test_app.app_context():
            user_dict = api.get_user(TEST_USER['s_number'])
            user = UserDB.create(**user_dict)
            user_dup_dict = api.get_user(TEST_USER['s_number'])
            user_dup = UserDB.create(**user_dup_dict)
            assert user is user_dup

    def test_list_all_users(self, test_app):
        with test_app.app_context():
            user1_dict = api.get_user(TEST_USER['s_number'])
            user2_dict = api.get_user(TEST_USER_NO_SDD['s_number'])
            user1 = UserDB.create(**user1_dict)
            user2 = UserDB.create(**user2_dict)

            user_list = UserDB.list_all()

            assert len(user_list) == 2  # Make sure exactly two users are returned

            # Make sure all users are in the list and it is sorted correctly
            if user1.id < user2.id:  # id of user1 is lower, so user1 must appear first in the list
                assert user1 == user_list[0]
                assert user2 == user_list[1]
            else:  # id of user2 is lower so it must appear first in the list
                assert user2 == user_list[0]
                assert user1 == user_list[1]

import pytest
import copy

from streeplijst2.database import UserController
import streeplijst2.api as api
from streeplijst2.config import TEST_USER, TEST_USER_NO_SDD

from datetime import datetime

# Add some extra fields to the test user
TEST_USER_1 = copy.deepcopy(TEST_USER)
TEST_USER_1.update(dict({
    'date_of_birth': datetime.fromisocalendar(2000, 1, 1),
    'has_sdd_mandate': True,
    'profile_picture': None
}))

# Create a duplicate object (deep copy so they do not reference the same object)
TEST_USER_DUP = copy.deepcopy(TEST_USER_1)

# Create a user with extra unnecessary fields
TEST_USER_EXTRA_FIELDS = copy.deepcopy(TEST_USER_1)
TEST_USER_EXTRA_FIELDS['email'] = 'hello@world.com'

# Create a user which has some fields which differ from the regular test user
TEST_USER_UPDATED = dict({
    's_number': 's9999990',
    'first_name': 'Test2',
    'last_name_prefix': 'the',
    'last_name': 'Testuser2',
    'date_of_birth': datetime.fromisocalendar(2001, 2, 2),
    'has_sdd_mandate': False,
})

# Create a second test user and add some important fields
TEST_USER_2 = TEST_USER_NO_SDD
TEST_USER_2.update(dict({
    'date_of_birth': datetime.fromisocalendar(2000, 1, 1),
    'has_sdd_mandate': True,
    'profile_picture': None
}))


class TestUser:

    def test_create_user(self, test_app):
        with test_app.app_context():
            user = UserController.create(**TEST_USER_1)
            for (key, value) in TEST_USER_1.items():  # Make sure all fields are stored correctly
                assert user.__getattribute__(key) == value

    def test_create_user_extra_fields(self, test_app):
        with test_app.app_context():
            user = UserController.create(**TEST_USER_EXTRA_FIELDS)  # Create a user with fields which are not needed
            required_fields = ((key, value) for (key, value) in TEST_USER_EXTRA_FIELDS.items() if key != 'email')
            for (key, value) in required_fields:  # Make sure all fields are stored correctly
                assert user.__getattribute__(key) == value
            assert hasattr(user, 'email') is False

    def test_create_user_duplicate(self, test_app):
        with test_app.app_context():
            user = UserController.create(**TEST_USER_1)
            duplicate_user = UserController.create(**TEST_USER_DUP)
            assert user is duplicate_user  # Make sure the same user is referenced in case of a duplicate

    def test_get_user(self, test_app):
        with test_app.app_context():
            user = UserController.create(**TEST_USER_1)
            other_user = UserController.get(TEST_USER_1['id'])
            assert user is other_user  # Make sure both objects are the same instance

    def test_get_user_by_s_number(self, test_app):
        with test_app.app_context():
            user = UserController.create(**TEST_USER_1)
            other_user = UserController.get_by_s_number(TEST_USER_1['s_number'])
            assert user is other_user  # Make sure both objects are the same instance

    def test_update_user(self, test_app):
        with test_app.app_context():
            user = UserController.create(**TEST_USER_1)
            updated_user = UserController.update(TEST_USER_1['id'], **TEST_USER_UPDATED)
            for (key, value) in TEST_USER_UPDATED.items():  # Make sure all values are updated as expected
                assert updated_user.__getattribute__(key) == value
                assert user.__getattribute__(key) == updated_user.__getattribute__(key)

    def test_delete_user(self, test_app):
        with test_app.app_context():
            user = UserController.create(**TEST_USER_1)
            get_user = UserController.get(TEST_USER_1['id'])
            assert get_user is not None  # Make sure the user is retrieved

            deleted_user = UserController.delete(TEST_USER_1['id'])
            assert user is deleted_user  # Make sure the same object is referenced

            get_user = UserController.get(TEST_USER_1['id'])
            assert get_user is None  # Make sure the user is not retrieved

    def test_list_all_users(self, test_app):
        with test_app.app_context():
            user2 = UserController.create(**TEST_USER_2)
            user1 = UserController.create(**TEST_USER_1)
            user_list = UserController.list_all()
            assert len(user_list) == 2  # Make sure exactly two users are returned
            assert user1 == user_list[0]  # Make sure each user is in the list
            assert user2 == user_list[1]  # Also make sure the order is correct (ascending id)


class TestUserFromAPI:
    """
    Integration tests between the database and api.
    """

    def test_get_user(self, test_app):
        with test_app.app_context():
            user_dict = api.get_user(TEST_USER['s_number'])
            user = UserController.create(**user_dict)
            for (key, value) in TEST_USER.items():  # Make sure all fields are stored correctly
                assert user.__getattribute__(key) == value

    def test_get_user_duplicate(self, test_app):
        with test_app.app_context():
            user_dict = api.get_user(TEST_USER['s_number'])
            user = UserController.create(**user_dict)
            user_dup_dict = api.get_user(TEST_USER['s_number'])
            user_dup = UserController.create(**user_dup_dict)
            assert user is user_dup

    def test_list_all_users(self, test_app):
        with test_app.app_context():
            user1_dict = api.get_user(TEST_USER['s_number'])
            user2_dict = api.get_user(TEST_USER_NO_SDD['s_number'])
            user1 = UserController.create(**user1_dict)
            user2 = UserController.create(**user2_dict)

            user_list = UserController.list_all()

            assert len(user_list) == 2  # Make sure exactly two users are returned

            # Make sure all users are in the list and it is sorted correctly
            if user1.id < user2.id:  # id of user1 is lower, so user1 must appear first in the list
                assert user1 == user_list[0]
                assert user2 == user_list[1]
            else:  # id of user2 is lower so it must appear first in the list
                assert user2 == user_list[0]
                assert user1 == user_list[1]

# def test_create_user(test_app):
#     with test_app.app_context():
#         user = db_controller.create_user(s_number=TEST_USER['s_number'])
#         assert user.id == TEST_USER['id']  # Test if there are items in the folder
#         assert user.first_name == TEST_USER['first_name']  # Test if a field is set
#         assert user.has_sdd_mandate is True  # Test if the user is SDD signed
#
#
# def test_user_from_api_errors(test_app):
#     with test_app.app_context():
#         # Non-existent user
#         incorrect_s_number = 's8888888'
#         with pytest.raises(UserNotFoundException) as err:
#             user = db_controller.create_user(s_number=incorrect_s_number)
#         assert '404 Client Error: User ' + incorrect_s_number + ' is not found' in str(err.value)
#
#         # Timeout error
#         with pytest.raises(Timeout) as err:
#             user = db_controller.create_user(s_number=TEST_USER['s_number'], timeout=0.001)
#
#
# def test_sync_user(test_app):
#     with test_app.app_context():
#         user = db_controller.create_user(s_number=TEST_USER['s_number'])
#         db_controller.sync_user(s_number=TEST_USER['s_number'], auto_commit=True)
#
#
# def test_get_or_create_user(test_app):
#     with test_app.app_context():
#         user = db_controller.get_or_create_user(s_number=TEST_USER['s_number'], auto_commit=True)
#         assert user is not None
#
#         user2 = db_controller.get_or_create_user(s_number=TEST_USER['s_number'], sync=False, auto_commit=True)
#         assert user is user2
#
#         user3 = db_controller.get_or_create_user(s_number=TEST_USER['s_number'], sync=True, auto_commit=True)
#         assert user is user3
#
#
# def test_get_user(test_app):
#     with test_app.app_context():
#         user = db_controller.get_user(user_id=TEST_USER['id'])
#         assert not user  # Ensure the user does not exist in the database
#
#         user = db_controller.create_user(s_number=TEST_USER['s_number'])
#         assert user
#         assert db_controller.get_user(user_id=TEST_USER['id'])  # Ensure the user exists in the database
#         assert db_controller.get_user(s_number=TEST_USER['s_number'])
#
#         # Test wrong input arguments
#         with pytest.raises(TypeError) as e:
#             db_controller.get_user()
#         with pytest.raises(TypeError) as e:
#             db_controller.get_user(user_id=TEST_USER['id'], s_number=TEST_USER['s_number'])
#
#
# # def test_upsert(test_app):
# #     """
# #     Tests that an existing user is updated from the database correctly.
# #     """
# #     with test_app.app_context():
# #         user = db_controller.create_user(TEST_USER['s_number'])  # Create a test user
# #         old_first_name = user.first_name  # Store the first name
# #
# #         updated_user = db_controller.create_user(TEST_USER['s_number'])  # Create another test user
# #         updated_first_name = user.first_name + 'extra'  # Create an updated first name
# #         updated_user.first_name = updated_first_name  # change the user first name to another value
# #
# #         assert user.id == updated_user.id  # Make sure the user IDs are equal so that the update functionality is used.
# #         assert user.first_name != updated_user.first_name  # Make sure the first names are not equal.
# #
# #         db_controller.upsert(user)  # Add the user to the database
# #         user1_from_db = db_controller.get_user(TEST_USER['s_number'])  # Get the user from the database
# #         assert user1_from_db.id == updated_user.id == user.id
# #         assert user1_from_db.first_name == user.first_name
# #         assert user1_from_db.first_name != updated_user.first_name  # Make sure the first name is not updated yet
# #
# #         db_controller.upsert(updated_user)  # Try to add the user again with updated fields.
# #         user1_from_db = db_controller.get_user(TEST_USER['s_number'])  # Get the user from the database
# #
# #         assert user1_from_db.id == updated_user.id
# #         assert user1_from_db.first_name == updated_user.first_name  # Make sure the first name is updated
# #         assert user1_from_db.first_name != old_first_name

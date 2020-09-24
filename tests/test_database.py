import pytest
from requests.exceptions import Timeout

from streeplijst2.api import FolderNotFoundException, UserNotFoundException
from streeplijst2.streeplijst.database import StreeplijstDBController as db_controller
from streeplijst2.config import TEST_USER, FOLDERS, TEST_ITEM, TEST_FOLDER_ID


def test_create_user(test_app):
    with test_app.app_context():
        user = db_controller.create_user(s_number=TEST_USER['s_number'])
        assert user.id == TEST_USER['id']  # Test if there are items in the folder
        assert user.first_name == TEST_USER['first_name']  # Test if a field is set
        assert user.has_sdd_mandate is True  # Test if the user is SDD signed


def test_user_from_api_errors(test_app):
    with test_app.app_context():
        # Non-existent user
        incorrect_s_number = 's8888888'
        with pytest.raises(UserNotFoundException) as err:
            user = db_controller.create_user(s_number=incorrect_s_number)
        assert '404 Client Error: User ' + incorrect_s_number + ' is not found' in str(err.value)

        # Timeout error
        with pytest.raises(Timeout) as err:
            user = db_controller.create_user(s_number=TEST_USER['s_number'], timeout=0.001)


def test_sync_user(test_app):
    with test_app.app_context():
        user = db_controller.create_user(s_number=TEST_USER['s_number'])
        db_controller.sync_user(s_number=TEST_USER['s_number'], auto_commit=True)


def test_get_or_create_user(test_app):
    with test_app.app_context():
        user = db_controller.get_or_create_user(s_number=TEST_USER['s_number'], auto_commit=True)
        assert user is not None

        user2 = db_controller.get_or_create_user(s_number=TEST_USER['s_number'], sync=False, auto_commit=True)
        assert user is user2

        user3 = db_controller.get_or_create_user(s_number=TEST_USER['s_number'], sync=True, auto_commit=True)
        assert user is user3


def test_get_user(test_app):
    with test_app.app_context():
        user = db_controller.get_user(user_id=TEST_USER['id'])
        assert not user  # Ensure the user does not exist in the database

        user = db_controller.create_user(s_number=TEST_USER['s_number'])
        assert user
        assert db_controller.get_user(user_id=TEST_USER['id'])  # Ensure the user exists in the database
        assert db_controller.get_user(s_number=TEST_USER['s_number'])

        # Test wrong input arguments
        with pytest.raises(TypeError) as e:
            db_controller.get_user()
        with pytest.raises(TypeError) as e:
            db_controller.get_user(user_id=TEST_USER['id'], s_number=TEST_USER['s_number'])


# def test_upsert(test_app):
#     """
#     Tests that an existing user is updated from the database correctly.
#     """
#     with test_app.app_context():
#         user = db_controller.create_user(TEST_USER['s_number'])  # Create a test user
#         old_first_name = user.first_name  # Store the first name
#
#         updated_user = db_controller.create_user(TEST_USER['s_number'])  # Create another test user
#         updated_first_name = user.first_name + 'extra'  # Create an updated first name
#         updated_user.first_name = updated_first_name  # change the user first name to another value
#
#         assert user.id == updated_user.id  # Make sure the user IDs are equal so that the update functionality is used.
#         assert user.first_name != updated_user.first_name  # Make sure the first names are not equal.
#
#         db_controller.upsert(user)  # Add the user to the database
#         user1_from_db = db_controller.get_user(TEST_USER['s_number'])  # Get the user from the database
#         assert user1_from_db.id == updated_user.id == user.id
#         assert user1_from_db.first_name == user.first_name
#         assert user1_from_db.first_name != updated_user.first_name  # Make sure the first name is not updated yet
#
#         db_controller.upsert(updated_user)  # Try to add the user again with updated fields.
#         user1_from_db = db_controller.get_user(TEST_USER['s_number'])  # Get the user from the database
#
#         assert user1_from_db.id == updated_user.id
#         assert user1_from_db.first_name == updated_user.first_name  # Make sure the first name is updated
#         assert user1_from_db.first_name != old_first_name

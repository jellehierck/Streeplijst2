import pytest

from streeplijst2.streeplijst import User
from streeplijst2.config import TEST_USER


def test_add_user(test_app):
    """
    Tests that a user is added to the database correctly.
    """
    with test_app.app_context():
        user1 = User.from_api(TEST_USER['s_number'])  # Create the test user
        User.add_or_update_user(user1)  # Add the user to the database

        user1_from_db = User.query.filter_by(s_number=TEST_USER['s_number']).first()  # Get the user from the database

        assert user1_from_db.id == user1.id  # Test that the users have the same parameters
        assert user1_from_db.first_name == user1.first_name


def test_update_user(test_app):
    """
    Tests that an existing user is updated from the database correctly.
    """
    old_first_name = ''
    updated_first_name = ''
    with test_app.app_context():
        user1 = User.from_api(TEST_USER['s_number'])  # Create a test user
        old_first_name = user1.first_name  # Store the first name

        updated_user = User.from_api(TEST_USER['s_number'])  # Create another test user
        updated_first_name = user1.first_name + 'extra'  # Create an updated first name
        updated_user.first_name = updated_first_name  # change the user first name to another value

        assert user1.id == updated_user.id  # Make sure the user IDs are equal so that the update functionality is used.
        assert user1.first_name != updated_user.first_name  # Make sure the first names are not equal.

        User.add_or_update_user(user1)  # Add the user to the database
        user1_from_db = User.query.filter_by(s_number=TEST_USER['s_number']).first()  # Get the user from the database
        assert user1_from_db.id == updated_user.id
        assert user1_from_db.first_name != updated_user.first_name  # Make sure the first name is not updated yet

        User.add_or_update_user(updated_user)  # Try to add the user again with updated fields.
        user1_from_db = User.query.filter_by(s_number=TEST_USER['s_number']).first()  # Return the user again

        assert user1_from_db.id == updated_user.id
        assert user1_from_db.first_name == updated_user.first_name  # Make sure the first name is updated
        assert user1_from_db.first_name != old_first_name

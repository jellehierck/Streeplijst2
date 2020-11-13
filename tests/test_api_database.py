import pytest

import streeplijst2.api as api
from streeplijst2.database import UserController

from streeplijst2.config import TEST_USER, TEST_USER_NO_SDD

"""
Integration tests between the database and api.
"""


def test_get_user(test_app):
    with test_app.app_context():
        user_dict = api.get_user(TEST_USER['s_number'])
        user = UserController.create(**user_dict)
        for (key, value) in TEST_USER.items():  # Make sure all fields are stored correctly
            assert user.__getattribute__(key) == value


def test_get_user_duplicate(test_app):
    with test_app.app_context():
        user_dict = api.get_user(TEST_USER['s_number'])
        user = UserController.create(**user_dict)
        user_dup_dict = api.get_user(TEST_USER['s_number'])
        user_dup = UserController.create(**user_dup_dict)
        assert user is user_dup


def test_list_all_users(test_app):
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

################
# Folder tests #
################



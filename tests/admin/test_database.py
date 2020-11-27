import pytest
import copy
from datetime import datetime

from flask_login import current_user as current_admin

from streeplijst2.admin.database import AdminDB
from streeplijst2.admin.models import Admin
from streeplijst2.config import DEFAULT_ADMIN

UPDATED_ADMIN = copy.deepcopy(DEFAULT_ADMIN)
UPDATED_ADMIN.update(dict({
    'name': 'updated_admin',
    'password': '1234567890',
    'active': False
}))

INCORRECT_PWD_ADMIN = copy.deepcopy(DEFAULT_ADMIN)
INCORRECT_PWD_ADMIN.update(dict({
    'password': '1234567890'
}))

INACTIVE_ADMIN = dict({
    'username': 's0000001',
    'password': '123456',
    'name': 'new_admin',
    'active': False
})


class TestAdmin:

    def test_create_admin(self, test_app):
        with test_app.app_context():
            admin = AdminDB.create(**DEFAULT_ADMIN)
            assert admin.username == DEFAULT_ADMIN['username']
            assert admin.active == DEFAULT_ADMIN['active']
            assert admin.last_accessed == datetime.min
            assert AdminDB.check_password(admin.username, DEFAULT_ADMIN['password'])  # Check if the password is stored

    def test_create_admin_existing(self, test_app):
        with test_app.app_context():
            admin = AdminDB.create(**DEFAULT_ADMIN)
            updated_admin = AdminDB.create(**UPDATED_ADMIN)
            assert updated_admin is admin  # Make sure they reference the same object, i.e. no new one was created
            assert updated_admin.name != UPDATED_ADMIN['name']  # Make sure the admin is not updated
            assert updated_admin.name == DEFAULT_ADMIN['name']
            assert AdminDB.check_password(updated_admin.username, DEFAULT_ADMIN['password'])
            assert not AdminDB.check_password(updated_admin.username, UPDATED_ADMIN['password'])

    def test_get_admin(self, test_app):
        with test_app.app_context():
            admin = AdminDB.create(**DEFAULT_ADMIN)
            get_admin = AdminDB.get(DEFAULT_ADMIN['username'])
            assert admin is get_admin

    def test_exists(self, test_app):
        with test_app.app_context():
            admin = AdminDB.create(**DEFAULT_ADMIN)
            exists = AdminDB.exists(admin.username)
            assert exists is True

    def test_get_by_id(self, test_app):
        with test_app.app_context():
            admin1 = AdminDB.create(**DEFAULT_ADMIN)
            admin2 = AdminDB.create(**INACTIVE_ADMIN)
            get_admin1 = AdminDB.get_by_id(1)  # IDs autoincrement, so the first admin should always get ID 1
            assert get_admin1 is admin1

            get_admin2 = AdminDB.get_by_id(2)
            assert get_admin2 is admin2

    def test_update_admin(self, test_app):
        """Test whether updating the unprotected datafields work"""
        with test_app.app_context():
            admin = AdminDB.create(**DEFAULT_ADMIN)
            previous_last_accessed = admin.last_accessed
            previous_updated = admin.updated

            updated_admin = AdminDB.update(**UPDATED_ADMIN, last_accessed=datetime.now())
            assert updated_admin.name != UPDATED_ADMIN['name']  # A protected field was not updated
            assert updated_admin.last_accessed > previous_last_accessed  # An unprotected field was updated
            assert updated_admin.updated > previous_updated

    def test_update_protected(self, test_app):
        with test_app.app_context():
            admin = AdminDB.create(**DEFAULT_ADMIN)
            previous_last_accessed = admin.last_accessed
            previous_updated = admin.updated

            updated_admin = AdminDB.update_protected(**UPDATED_ADMIN, last_accessed=datetime.now())
            assert updated_admin.name == UPDATED_ADMIN['name']  # Protected fields were updated
            assert updated_admin.active == UPDATED_ADMIN['active']
            assert not AdminDB.check_password(updated_admin.username, DEFAULT_ADMIN['password'])
            assert AdminDB.check_password(updated_admin.username, UPDATED_ADMIN['password'])

            assert updated_admin.last_accessed > previous_last_accessed  # An unprotected field was updated too
            assert updated_admin.updated > previous_updated

    def test_delete_admin(self, test_app):
        with test_app.app_context():
            admin = AdminDB.create(**DEFAULT_ADMIN)
            get_admin = AdminDB.get(DEFAULT_ADMIN['username'])
            assert get_admin is not None  # Make sure the admin exists in the database

            deleted_admin = AdminDB.delete(admin.username)
            assert deleted_admin is admin  # Make sure the deleted admin is still returned from the .delete() call

            get_admin = AdminDB.get(admin.username)
            assert get_admin is None  # The admin cannot be retrieved from the database anymore

    def test_list_all_admins(self, test_app):
        with test_app.app_context():
            admin1 = AdminDB.create(**DEFAULT_ADMIN)
            admin2 = AdminDB.create(**INACTIVE_ADMIN)
            admin_list = AdminDB.list_all()
            assert len(admin_list) == 2
            assert admin1 == admin_list[0]  # Make sure the admins are returned in order of insertion
            assert admin2 == admin_list[1]

    def test_check_password(self, test_app):
        with test_app.app_context():
            assert not AdminDB.check_password(DEFAULT_ADMIN['username'], DEFAULT_ADMIN['password'])  # Check None admin
            admin = AdminDB.create(**DEFAULT_ADMIN)
            assert AdminDB.check_password(admin.username, DEFAULT_ADMIN['password'])  # Check correct password
            assert not AdminDB.check_password(admin.username, INCORRECT_PWD_ADMIN['password'])  # Check wrong password

    def test_login_without_password(self, test_app):
        with test_app.test_request_context():  # Logging in and out is done in a request context, not the app context
            logged_in = AdminDB.login_without_password(DEFAULT_ADMIN['username'])  # Store the return value
            assert not logged_in  # Non-existent admins cannot log in

            inactive_admin = AdminDB.create(**INACTIVE_ADMIN)
            logged_in = AdminDB.login_without_password(inactive_admin.username)
            assert not logged_in  # Inactive admins cannot log in
            assert current_admin != inactive_admin  # Make sure there is no admin logged in yet

            active_admin = AdminDB.create(**DEFAULT_ADMIN)
            logged_in = AdminDB.login_without_password(active_admin.username)  # Log in the admin
            assert logged_in is True  # Admin should be logged in now
            assert current_admin == active_admin  # Make sure the logged in admin is an instance of Admin
            assert current_admin.username == active_admin.username  # Make sure the logged in admin is correct

    def test_login(self, test_app):
        with test_app.test_request_context():
            logged_in = AdminDB.login(DEFAULT_ADMIN['username'], DEFAULT_ADMIN['password'])  # Store the return value
            assert logged_in is False  # Non-existent admins cannot log in

            inactive_admin = AdminDB.create(**INACTIVE_ADMIN)
            logged_in = AdminDB.login(inactive_admin.username, INACTIVE_ADMIN['password'])
            assert logged_in is False  # Inactive admins cannot log in
            assert current_admin != inactive_admin  # Make sure there is no admin logged in yet

            active_admin = AdminDB.create(**DEFAULT_ADMIN)

            logged_in = AdminDB.login(active_admin.username, INCORRECT_PWD_ADMIN['password'])  # Log in with wrong pwd
            assert logged_in is False  # Incorrect password should not log the admin in
            assert current_admin != active_admin

            logged_in = AdminDB.login(active_admin.username, DEFAULT_ADMIN['password'])  # Log in the admin
            assert logged_in is True  # Admin should be logged in now
            assert current_admin == active_admin  # Make sure the logged in admin is an instance of Admin
            assert current_admin.username == active_admin.username  # Make sure the logged in admin is correct

    def test_login_force(self, test_app):
        with test_app.test_request_context():
            inactive_admin = AdminDB.create(**INACTIVE_ADMIN)
            logged_in = AdminDB.login(inactive_admin.username, INACTIVE_ADMIN['password'])
            assert logged_in is False  # Inactive admins cannot log in
            assert current_admin != inactive_admin  # Make sure there is no admin logged in yet

            logged_in = AdminDB.login(inactive_admin.username, INACTIVE_ADMIN['password'], force_active=True)
            assert logged_in is True  # Inactive admins cannot log in
            assert current_admin == inactive_admin  # Make sure there is no admin logged in yet

    def test_logout(self, test_app):
        with test_app.test_request_context():
            logged_in_admin = AdminDB.create(**DEFAULT_ADMIN)
            logged_in = AdminDB.login(logged_in_admin.username, DEFAULT_ADMIN['password'])  # Log in the admin
            assert logged_in is True
            assert current_admin == logged_in_admin

            AdminDB.logout()  # Logout any admins
            assert current_admin != logged_in_admin

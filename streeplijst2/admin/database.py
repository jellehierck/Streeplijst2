from sqlalchemy import asc
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user as login_admin  # Rename this function for readability
from flask_login import logout_user as logout_admin  # Rename this function for readability

from streeplijst2.admin.models import Admin
from streeplijst2.extensions import db


class AdminDB:

    @classmethod
    def check_password(cls, username: str, password: str) -> bool:
        """
        Check the password of the admin.

        :param username: Username to check.
        :param password: Unhashed password to check.
        :return: True if the password was correct, False if the admin does not exist or the password is incorrect.
        """
        admin = cls.get(username=username)  # Get the admin user
        if admin is not None:
            return check_password_hash(admin.password_hash, password)
        else:
            return False  # If the admin does not exist, the password is not correct of course

    @classmethod
    def login_without_password(cls, username: str) -> bool:
        """
        Logs in the admin with that username. The password is not checked during this method.

        :return: True if the login was successful, False if the admin was not active.
        """
        admin = cls.get(username=username)
        if admin is not None and admin.is_active is True:  # The admin exists and is active
            login_admin(admin)  # Log in the admin
            cls.update(username=username, last_accessed=datetime.now())
            return True
        return False  # The login attempt was not successful because the admin was not active or not found

    @classmethod
    def login(cls, username: str, password: str, force_active: bool = False) -> bool:
        """
        Log in an admin. If the admin does not exist, the password is incorrect or the admin is inactive, return False.

        :param username: Username of the admin to login. Usually this is the student number.
        :param password: Password of the admin.
        :param force_active: If set to True, the admin will be logged in even if it is inactive (password still needs to
        match).
        :return: True if the attempt was successful, False otherwise.
        """
        admin = cls.get(username=username)  # Get the admin user
        if admin is None:  # The admin does not exist in the database
            return False
        if admin.is_active is False and force_active is False:  # The admin is inactive and force is off
            return False
        if not cls.check_password(username=username, password=password):  # The password is incorrect
            return False

        login_admin(admin, force=force_active)  # All checks are passed, log in the admin
        cls.update(username=username, last_accessed=datetime.now())
        return True

    @classmethod
    def logout(cls) -> None:
        """Log out any logged in admin."""
        logout_admin()

    @classmethod
    def create(cls, username: str, name: str, password: str, active: bool = True) -> Admin:
        """
        Create a new admin user. If it exists already, return the existing admin without updating their fields.

        :param username: Username, a unique identifier. Usually this is the student number.
        :param name: Display name.
        :param password: Plaintext password.
        :param active: Whether the admin is active upon creation. Default: True.
        :return:
        """
        existing_admin = cls.get(username=username)
        if existing_admin is not None:
            return existing_admin

        # If the admin does not exist, create it
        password_hash = generate_password_hash(password)  # Hash the password
        new_admin = Admin(username=username, name=name, password_hash=password_hash, active=active)
        db.session.add(new_admin)
        db.session.commit()
        return new_admin

    @classmethod
    def get(cls, username: str) -> Admin:
        """
        Get an admin based on their username.

        :param username: The admin to retrieve.
        """
        return Admin.query.filter_by(username=username).first()  # Return the admin with that username

    @classmethod
    def get_by_id(cls, id: int) -> Admin:
        """
        Get an admin based on their ID.

        :param id: The ID To retrieve the admin by.
        """
        return Admin.query.get(id)  # Return the admin with that ID

    @classmethod
    def exists(cls, username: str) -> bool:
        """
        Return whether the admin exists in the database.

        :param username: Admin to check.
        """
        return cls.get(username=username) is not None  # Return whether the admin exists in the database

    @classmethod
    def list_all(cls) -> list:
        """
        List all admins.

        :return: A list of all admins.
        """
        return Admin.query.order_by(asc(Admin.id)).all()

    @classmethod
    def update(cls, username: str, **kwargs) -> Admin:
        """
        Update the admin unprotected fields ('last_accessed').

        :param username: Admin to modify.
        :param kwargs: Fields are updated with keyword arguments.
        :return: The updated admin.
        """
        modified_admin = cls.get(username=username)

        # If no kwarg is given for an attribute, set it to the already stored attribute
        modified_admin.last_accessed = kwargs.get('last_accessed', modified_admin.last_accessed)

        modified_admin.updated = datetime.now()
        db.session.commit()
        return modified_admin

    @classmethod
    def update_protected(cls, username: str, **kwargs) -> Admin:
        """
        Update all data fields of the admin ('name', 'active', 'password', 'last_accessed'). Note: to change
        'password_hash', a 'password' must be passed in the kwargs which is automatically hashed. No check is performed
        to see if this action is allowed, i.e. there is no authentication check.

        :param username: Admin to modify.
        :param kwargs: The fields are updated with keyword arguments.
        :return: The updated admin.
        """
        modified_admin = cls.get(username=username)

        # If no kwarg is given for an attribute, set it to the already stored attribute
        modified_admin.name = kwargs.get('name', modified_admin.name)
        modified_admin.active = kwargs.get('active', modified_admin.active)
        modified_admin.last_accessed = kwargs.get('last_accessed', modified_admin.last_accessed)

        # Change the password if a new password was provided
        password = kwargs.get('password', None)
        if password is not None:
            password_hash = generate_password_hash(password=password)
            modified_admin.password_hash = password_hash

        modified_admin.updated = datetime.now()
        db.session.commit()

        return modified_admin

    @classmethod
    def delete(cls, username: str) -> Admin:
        """
        Delete an admin. This action cannot be reversed.

        :param username: Admin to delete.
        :return: The deleted admin object.
        """
        deleted_admin = cls.get(username=username)
        db.session.delete(deleted_admin)
        db.session.commit()

        return deleted_admin

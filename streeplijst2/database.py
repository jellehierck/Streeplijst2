from streeplijst2.models import User
from streeplijst2.extensions import db

from sqlalchemy import asc

from datetime import datetime


def init_database(config=None) -> None:
    """
    Initialize any custom models for the database.

    :param config: If provided, use this config.
    """
    pass  # It is not needed to initialize any models from this module


class UserDB:

    @classmethod
    def create(cls, id: int, s_number: str, first_name: str, last_name: str, date_of_birth: datetime,
               last_name_prefix: str = None, has_sdd_mandate: bool = False, profile_picture: str = None,
               **kwargs) -> User:
        """
        Create a new user and store it in the database.

        :param id: Congressus user id.
        :param s_number: Student or Employee number (Congressus user name)
        :param first_name: First name.
        :param last_name: Last name.
        :param date_of_birth: Date of birth.
        :param last_name_prefix: Last name prefix (e.g. 'van der').
        :param has_sdd_mandate: Flag whether this user has signed their SDD mandate (required for making any purchase).
        :param profile_picture: URL to profile picture.
        :return: The newly created user.
        """
        if cls.get(id=id) is not None:  # Check if the user already exists, if so, update it
            return cls.update(id=id, s_number=s_number, first_name=first_name, last_name_prefix=last_name_prefix,
                              last_name=last_name, date_of_birth=date_of_birth, has_sdd_mandate=has_sdd_mandate,
                              profile_picture=profile_picture)

        # If the user does not exist yet, create it
        new_user = User(id=id, s_number=s_number, first_name=first_name, last_name_prefix=last_name_prefix,
                        last_name=last_name, date_of_birth=date_of_birth, has_sdd_mandate=has_sdd_mandate,
                        profile_picture=profile_picture)
        db.session.add(new_user)
        db.session.commit()
        return new_user

    @classmethod
    def update(cls, id: int, **kwargs) -> User:
        """
        Update a user's data fields.

        :param id: The id of the user to update.
        :param kwargs: The fields are updated with keyword arguments.
        :return: The updated user.
        """
        modified_user = User.query.get(id)

        # If no kwarg is given for an attribute, set it to the already stored attribute
        modified_user.s_number = kwargs.get('s_number', modified_user.s_number)
        modified_user.first_name = kwargs.get('first_name', modified_user.first_name)
        modified_user.last_name_prefix = kwargs.get('last_name_prefix', modified_user.last_name_prefix)
        modified_user.last_name = kwargs.get('last_name', modified_user.last_name)
        modified_user.date_of_birth = kwargs.get('date_of_birth', modified_user.date_of_birth)
        modified_user.has_sdd_mandate = kwargs.get('has_sdd_mandate', modified_user.has_sdd_mandate)
        modified_user.profile_picture = kwargs.get('profile_picture', modified_user.profile_picture)

        modified_user.updated = datetime.now()
        db.session.commit()

        return modified_user

    @classmethod
    def delete(cls, id: int) -> User:
        """
        Delete a user.

        :param id: ID of the user to delete.
        :return: The deleted user.
        """
        deleted_person = User.query.get(id)
        db.session.delete(deleted_person)
        db.session.commit()

        return deleted_person

    @classmethod
    def list_all(cls) -> list:
        """
        List all users.

        :return: A List of all users.
        """
        # TODO: Add a way to sort result differently
        return User.query.order_by(asc(User.id)).all()

    @classmethod
    def get(cls, id: int) -> User:
        """
        Return the user with that id.

        :param id: The id to get the user by.
        :return: The user.
        """
        return User.query.get(id)

    @classmethod
    def get_by_s_number(cls, s_number: str) -> User:
        """
        Return the user with that s_number.

        :param s_number: The student or employee number to get the user by.
        :return: The user.
        """
        return User.query.filter_by(s_number=s_number).first()

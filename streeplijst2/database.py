from streeplijst2.models import User
from streeplijst2.extensions import db
import streeplijst2.api as api
from streeplijst2.config import TIMEOUT


class DBController:

    @staticmethod
    def commit():
        """Commits al changes to the database."""
        db.session.commit()

    @classmethod
    def add(cls, obj: object, auto_commit: bool = False):
        """
        Adds an object to the database session.

        :param obj: The object to add to the database.
        :param auto_commit: When set to True, commits the changes to the database at the end of the method call.
        """
        db.session.add(obj)
        if auto_commit is True:
            cls.commit()

    @classmethod
    def create_user(cls, s_number: str, timeout: float = TIMEOUT, auto_commit=True) -> User:
        """
        Create a user from an API call.

        :param s_number: Student or Employee number (Congressus user name)
        :param timeout: Timeout for the post request. Defaults to config.py TIMEOUT.
        """
        user_details = api.get_user(s_number, timeout=timeout)  # GET all user details from the API
        user = User(s_number, id=user_details['id'], date_of_birth=user_details['date_of_birth'],
                    first_name=user_details['first_name'], last_name=user_details['primary_last_name_main'],
                    last_name_prefix=user_details['primary_last_name_prefix'],
                    has_sdd_mandate=user_details['has_sdd_mandate'], profile_picture=user_details['profile_picture'])
        cls.add(user, auto_commit=auto_commit)  # Add the user to the database
        return user  # Return the user

    @staticmethod
    def get_user(user_id: int = None, s_number: str = None) -> User:
        """
        Get a user from the database. If it does not exist, return None. A user can be searched for by using their
        user_id or s_number, but not both.

        :param user_id: User ID
        :param s_number: Student number
        :return: The User instance.
        """
        if user_id is not None and s_number is None:
            return User.query.filter_by(id=user_id).first()
        elif s_number is not None and user_id is None:
            return User.query.filter_by(s_number=s_number).first()
        elif user_id is not None and s_number is not None:
            raise TypeError("get_user expected exactly 1 input argument, got 2.")
        else:
            raise TypeError("get_user expected exactly 1 input argument, got 0.")

    @classmethod
    def get_or_create_user(cls, s_number: str, sync: bool = True, timeout: float = TIMEOUT,
                           auto_commit: bool = False) -> User:
        """
        Get the user from the database, or create it if it does not exist in the database yet.

        :param s_number: Student number
        :param sync: When set to True, this will also synchronize the user with API.
        :param timeout: Timeout for the get request. Defaults to config.py TIMEOUT.
        :param auto_commit: When set to True, commits the changes to the database at the end of the method call.
        :return: The requested user.
        """
        user = cls.get_user(s_number=s_number)
        if user:  # If the user exists already
            if sync is True:  # Synchronize the user with the API if the flag is true
                cls.sync_user(s_number=s_number, timeout=timeout, auto_commit=False)
        else:  # The user did not exist already, so it needs to be created
            user = cls.create_user(s_number=s_number, timeout=timeout, auto_commit=False)

        if auto_commit is True:
            cls.commit()
        return user

    @classmethod
    def sync_user(cls, s_number: str, timeout: float = TIMEOUT, auto_commit: bool = False):
        user = cls.get_user(s_number=s_number)
        if user:  # If the user exists, update it from the API
            api_mapping = api.get_user(s_number=s_number, timeout=timeout)  # Get a dict from the API
            user.update(**api_mapping)  # Convert the dict to keyword arguments using ** and update
        else:
            pass  # TODO: Insert a proper exception here

        if auto_commit is True:
            cls.commit()

    @classmethod
    def upsert(cls, obj: db.Model, auto_commit=False):  # TODO: Replace db.Model with DBBase class
        """
        Upserts (Updates/Inserts) an object into the connected database.

        :param obj: The object to upsert
        :param auto_commit: When set to True, commits the changes to the database at the end of the method call. This
        should only be done at the end of all database additions/alterations.
        """
        obj_class = type(obj)  # Determine the class of this object (should be a SQLAlchemy Model)
        if obj in db.session:  # If the object is found, update its fields
            local_obj = obj_class.query.filter_by(id=obj.id).first()  # Try to find the object in the database
            local_obj.update(obj)
        else:  # If the object is not found, add it to the database
            db.session.add(obj)

        # TODO: Add an update for the obj.last_updated here when DBBase class is implemented

        if auto_commit:  # Commit if the auto_commit flag is true
            cls.commit()

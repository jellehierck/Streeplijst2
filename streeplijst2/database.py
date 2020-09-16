from datetime import timedelta, datetime

from streeplijst2.streeplijst import Folder, User, Sale, Item
from streeplijst2.extensions import db
import streeplijst2.api as api
from streeplijst2.config import FOLDERS, TIMEOUT


class LocalDBController:

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
    def create_folder(cls, folder_id: int = None, mapping: dict = None, timeout: float = TIMEOUT,
                      auto_commit=True) -> Folder:
        """
        Reads config.py and returns a single Folder object with the specified name.

        :param folder_id: The folder id to read.
        :param timeout: Timeout for the post request. Defaults to config.py TIMEOUT.
        :return: The Folder object
        """
        if folder_id is not None:
            folder_config = FOLDERS[folder_id]  # Load the folder configuration
        elif mapping is not None:
            folder_config = {'name': '', 'id': 1, 'media': '', }  # Set a default dict for the folder configuration
            folder_config.update(mapping)  # Replace the default dict values with the passed in kwargs
        else:
            raise TypeError("create_folder expected at least a folder_id or a dictionary with mapping, got None.")
        folder = Folder(folder_config['name'], folder_config['id'], folder_config['media'])  # Create Folder object
        cls.add(folder, auto_commit=True)  # Add and commit the unfinished folder

        # Populate the folder with items and commit to the database
        cls.sync_folder(folder_id=folder.id, force_sync=True, timeout=timeout, auto_commit=auto_commit)
        return folder  # Return the folder

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

    @classmethod
    def create_item(cls, item_id: int, timeout: float = TIMEOUT, auto_commit=True) -> Item:
        """
        Create an item from an API call.

        :param item_id: Item ID
        :param timeout: Timeout for the post request. Defaults to config.py TIMEOUT.
        """
        item_details = api.get_product(item_id=item_id, timeout=timeout)  # GET all item details from the API
        item = Item(name=item_details['name'], id=item_details['id'], price=item_details['price'], folder=None,
                    folder_id=item_details['folder_id'], published=item_details['published'],
                    media=item_details['media'])
        cls.add(item, auto_commit=auto_commit)  # Add the item to the database
        return item  # Return the item

    @classmethod
    def create_sale(cls, item_id: int, user_id: int, quantity: int, auto_commit=True) -> Sale:
        """
        Create an item from an API call.

        :param item_id: Item ID
        :param user_id: User ID (not username)
        :param quantity: Quantity of the item to buy
        """
        item = cls.get_item(item_id)  # Retrieve the item from the database
        user = cls.get_user(user_id)  # Retrieve the user from the database

        if not item or not user:  # If the item or the user do not exist in the database, return None
            return None  # TODO: Change this exception

        sale = Sale(user, item, quantity)  # Create the sale
        cls.add(sale, auto_commit=auto_commit)  # Add the sale to the database
        return sale  # Return the sale

    @staticmethod
    def get_item(item_id: int) -> Item:
        """
        Get an item from the database

        :param item_id: Item ID
        :return: The Item instance
        """
        return Item.query.filter_by(id=item_id).first()

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
    def get_folder(cls, folder_id: int, sync: bool = False, force_sync: bool = True, update_interval=10,
                   timeout: float = TIMEOUT, auto_commit: bool = False) -> Folder:
        """
        Return a folder from the database. If no folder was found, return None

        :param folder_id: The folder to sync
        :param sync: When set to True, the folder will be synced with the API before being returned.
        :param force_sync: When set to True, the folder is synced with the API regardless of folder.last_synchronized.
        :param update_interval: The time in minutes the folder should be out of sync before it is updated. If
        datetime.now() - folder.last_synchronized > update_interval, the folder is synced with the API.
        :param timeout: Timeout for the get request. Defaults to config.py TIMEOUT.
        :param auto_commit: When set to True, commits the changes to the database at the end of the method call.
        :return: The folder. If no folder was found, return None.
        """
        folder = Folder.query.filter_by(id=folder_id).first()
        if folder:  # If a folder was found
            if sync is True:  # If the folder should be synchronized with the API
                cls.sync_folder(folder.id, force_sync=force_sync, update_interval=update_interval, timeout=timeout,
                                auto_commit=auto_commit)
        return folder

    @classmethod
    def get_or_create_folder(cls, folder_id: int = None, sync: bool = False, force_sync: bool = True,
                             update_interval=10, timeout: float = TIMEOUT, auto_commit: bool = False) -> Folder:
        """
        Get the folder from the database, or create it if it does not exist in the database.

        :param folder_id: Folder ID to retrieve
        :param sync: When set to True, the folder will be synced with the API before being returned.
        :param force_sync: When set to True, the folder is synced with the API regardless of folder.last_synchronized.
        :param update_interval: The time in minutes the folder should be out of sync before it is updated. If
        datetime.now() - folder.last_synchronized > update_interval, the folder is synced with the API.
        :param timeout: Timeout for the get request. Defaults to config.py TIMEOUT.
        :param auto_commit: When set to True, commits the changes to the database at the end of the method call.
        :return: The folder.
        """
        folder = cls.get_folder(folder_id=folder_id, sync=sync, force_sync=force_sync, update_interval=update_interval,
                                timeout=timeout, auto_commit=False)
        if not folder:
            folder = cls.create_folder(folder_id=folder_id, timeout=timeout, auto_commit=False)

        if auto_commit is True:
            cls.commit()
        return folder

    @staticmethod
    def get_sale(sale_id: int) -> Sale:
        """
        Return a sale from the database.

        :param sale_id: Sale ID. This is the local ID.
        :return: The Sale instance
        """
        # TODO: Be able to search for sales by date, item, user or api_id
        return Sale.query.filter_by(id=sale_id).first()

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

    @classmethod
    def sync_folder(cls, folder_id, force_sync: bool = True, update_interval=10, timeout: float = TIMEOUT,
                    auto_commit: bool = False) -> None:
        """
        GET all items from Congressus, update the folder.items list and return a dict of all items.

        :param folder_id: The folder to sync
        :param force_sync: When set to True, the folder is synced with the API regardless of folder.last_synchronized.
        :param update_interval: The time in minutes the folder should be out of sync before it is updated. If
        datetime.now() - folder.last_synchronized > update_interval, the folder is synced with the API.
        :param timeout: Timeout for the get request. Defaults to config.py TIMEOUT.
        :param auto_commit: When set to True, commits the changes to the database at the end of the method call.
        """
        folder = cls.get_folder(folder_id, sync=False)
        if not folder:
            return  # TODO: Put in a fitting FolderNotInDatabaseException

        td = timedelta(minutes=update_interval)
        if force_sync or (datetime.now() - folder.last_synchronized) > td:  # If the folder should update
            items_list = api.get_products_in_folder(folder.id, timeout=timeout)  # get items in the folder from API
            for item_dict in items_list:  # Iterate all items in the response
                item = folder.get_item(item_dict['id'])  # Get the item from the folder
                if not item:
                    # If the item was not found in the folder, create a new one. It is linked with the folder upon
                    # initialization.
                    item = Item(name=item_dict['name'], id=item_dict['id'], price=item_dict['price'], folder=folder,
                                folder_id=item_dict['folder_id'], published=item_dict['published'],
                                media=item_dict['media'])
                else:  # If an item was found, update the item fields
                    item.update(name=item_dict['name'], id=item_dict['id'], price=item_dict['price'], folder=folder,
                                folder_id=item_dict['folder_id'], published=item_dict['published'],
                                media=item_dict['media'])
            folder.last_synchronized = datetime.now()  # Set the last updated time to now

        if auto_commit is True:
            cls.commit()
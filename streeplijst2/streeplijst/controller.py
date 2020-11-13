from datetime import datetime, timedelta

from streeplijst2.streeplijst.database import ItemDB, FolderDB, SaleDB
from streeplijst2.streeplijst.models import Folder, Item
import streeplijst2.api as api


class FolderNotInDatabaseException(Exception):  # TODO: Add a streeplijst base exception module
    """Error when a folder could not be loaded from the database."""


class StreeplijstController:
    UPDATE_INTERVAL = 60 * 60 * 4  # Nr of seconds between automatic updates (default 4 hours)

    @classmethod
    def add_or_update_folder(cls, **kwargs) -> Folder:
        """
        Add a folder to the database or update it if it already exists.  See FolderDB.create() for more information.

        :param kwargs: Folder fields.
        :return: The Folder instance.
        """
        return FolderDB.create(**kwargs)

    @classmethod
    def load_folder(cls, folder_id: int, force_update: bool = False,
                    auto_update_interval: int = UPDATE_INTERVAL) -> Folder:
        """
        Load a folder from the database or from the API. The database is much faster. The database is much faster but
        may be out of sync with the API.

        :param folder_id: Folder ID to retrieve.
        :param force_update: When set to True, the folder will update its contents from the API.
        :param auto_update_interval: Alternative update interval (defaults to cls.UPDATE_INTERVAL).
        :return: The Folder instance.
        """
        folder = FolderDB.get(folder_id)
        if folder is None:  # The folder was not in the database
            raise FolderNotInDatabaseException("Folder not in local database. Add it using .add_or_update_folder()")

        # Check if the folder contents should be updated.
        update_threshold = datetime.now() - timedelta(seconds=auto_update_interval)
        if force_update is True or folder.updated < update_threshold:
            items = api.get_products_in_folder(folder.id)
            for item_dict in items:  # Update existing items or create a new item if it did not exist in db before
                item = ItemDB.create(**item_dict)
            FolderDB.update(folder.id, synchronized=datetime.now())  # Update the timed folder fields.

        return folder

    @classmethod
    def load_folder_items(cls, folder_id: int, force_update: bool = False,
                          auto_update_interval: int = UPDATE_INTERVAL) -> list:
        """
        Load all items in a folder from the database or from the API. The database is much faster but may be out of sync
        with the API.

        :param folder_id: Folder ID to retrieve items from.
        :param force_update: When set to True, the folder will update its contents from the API.
        :param auto_update_interval: Alternative update interval (defaults to cls.UPDATE_INTERVAL).
        :return: A list of Items in the folder.
        """
        folder = FolderDB.get(folder_id)
        if folder is None:  # The folder was not in the database
            raise FolderNotInDatabaseException("Folder not in local database. Add it using .add_or_update_folder()")

        # Check if the folder contents should be updated.
        update_threshold = datetime.now() - timedelta(seconds=auto_update_interval)
        if force_update is True or folder.updated < update_threshold:
            items = api.get_products_in_folder(folder.id)
            for item_dict in items:  # Update existing items or create a new item if it did not exist in db before
                item = ItemDB.create(**item_dict)
            FolderDB.update(folder.id, synchronized=datetime.now())  # Update the timed folder fields.

        return FolderDB.get_items_in_folder(folder.id)

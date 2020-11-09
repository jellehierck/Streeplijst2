from datetime import datetime

from sqlalchemy import asc

from streeplijst2.streeplijst.models import Folder, Sale, Item
from streeplijst2.extensions import db


class ItemController:

    @classmethod
    def create(cls, id: int, name: str, price: int, published: bool, folder_id: int, folder_name: int,
               media: str = None) -> Item:
        """
        Instantiate an Item object and store it in the database. This Item contains only relevant information provided
        by the API response.

        :param name: Item name.
        :param id: Item id.
        :param price: Item price in cents.
        :param folder_id: Folder id.
        :param folder_name: Folder name.
        :param published: True if the item is published, False otherwise.
        :param media: (optional) Image URL.
        """
        if cls.get(id=id) is not None:  # Check if the item already exists, if so, update and return it
            return cls.update(id=id, name=name, price=price, published=published, media=media, folder_id=folder_id,
                              folder_name=folder_name)

        # If the item does not exist yet, create it
        new_item = Item(id=id, name=name, price=price, published=published, media=media, folder_id=folder_id,
                        folder_name=folder_name)
        db.session.add(new_item)
        db.session.commit()
        return new_item

    @classmethod
    def update(cls, id: int, **kwargs) -> Item:
        """
        Update this item's data fields.

        :param id: The item ID of the item to update.
        :param kwargs: The fields are updated with keyword arguments.
        :return: The updated item.
        """
        modified_item = Item.query.get(id=id)

        # If no kwarg is given for an attribute, set it to the already stored attribute
        modified_item.name = kwargs.get('name', modified_item.name)
        modified_item.id = kwargs.get('id', modified_item.id)
        modified_item.price = kwargs.get('price', modified_item.price)
        modified_item.folder = kwargs.get('folder', modified_item.folder)
        modified_item.folder_id = kwargs.get('folder_id', modified_item.folder_id)
        modified_item.published = kwargs.get('published', modified_item.published)
        modified_item.media = kwargs.get('media', modified_item.media)

        modified_item.updated = datetime.now()
        db.session.commit()

        return modified_item

    @classmethod
    def delete(cls, id: int) -> Item:
        """
        Delete an item.

        :param id: ID of the item to delete.
        :return: The deleted item.
        """
        deleted_item = Item.query.get(id=id)
        db.session.delete(deleted_item)
        db.session.commit()

        return deleted_item

    @classmethod
    def list_all(cls) -> list:
        """
        List all items sorted by id.

        :return: A List of all items.
        """
        # TODO: Add a way to sort result differently
        return Item.query.order_by(asc(id=Item.id)).all()

    @classmethod
    def get(cls, id: int) -> Item:
        """
        Return the item with that id.

        :param id: The id to get the item by.
        :return: The item.
        """
        return Item.query.get(id=id)

    @classmethod
    def get_by_folder_id(cls, folder_id: int) -> list:
        """
        Return the items in the folder with that id.

        :param folder_id: The folder id to get items by.
        :return: A List of items.
        """
        return Item.query.filter_by(folder_id=folder_id).all()


class FolderController:

    @classmethod
    def create(cls, id: int, name: str, media: str = None) -> Folder:
        """
        Instantiate a Folder object and store it in the database.

        :param name: Folder name.
        :param id: Folder id.
        :param media: (optional) Image URL.
        :return: The folder.
        """
        if cls.get(id=id) is not None:  # Check if the folder already exists, if so, update and return it
            return cls.update(id=id, name=name, media=media)

        # If the folder does not exist yet, create it
        new_folder = Folder(id=id, name=name, media=media)
        db.session.add(new_folder)
        db.session.commit()
        return new_folder

    @classmethod
    def update(cls, id: int, **kwargs) -> Folder:
        """
        Update this folder's data fields.

        :param id: The item ID of the folder to update.
        :param kwargs: The fields are updated with keyword arguments.
        :return: The updated folder.
        """
        modified_folder = Item.query.get(id=id)

        # If no kwarg is given for an attribute, set it to the already stored attribute
        modified_folder.name = kwargs.get('name', modified_folder.name)
        modified_folder.id = kwargs.get('id', modified_folder.id)
        modified_folder.media = kwargs.get('media', modified_folder.media)

        modified_folder.updated = datetime.now()
        db.session.commit()

        return modified_folder

    @classmethod
    def delete(cls, id: int) -> Folder:
        """
        Delete a folder.

        :param id: ID of the folder to delete.
        :return: The deleted folder.
        """
        deleted_folder = Folder.query.get(id=id)
        db.session.delete(deleted_folder)
        db.session.commit()

        return deleted_folder

    @classmethod
    def list_all(cls) -> list:
        """
        List all folders sorted by id.

        :return: A List of all folders.
        """
        # TODO: Add a way to sort result differently
        return Folder.query.order_by(asc(id=Folder.id)).all()

    @classmethod
    def get(cls, id: int) -> Folder:
        """
        Return the folder with that id.

        :param id: The id to get the folder by.
        :return: The folder.
        """
        return Folder.query.get(id=id)


class SaleController:

    @classmethod
    def create(cls, quantity: int, total_price: int, item_id: int, item_name: str, user_id: int,
               user_s_number: str) -> Sale:
        """
        Instantiate a Sale object and store it in the database.

        :param quantity: Amount of the item to buy.
        :param total_price: Total price (quantity * item.price).
        :param item_id: Item ID.
        :param item_name: Item name.
        :param user_id: User ID.
        :param user_s_number: User s_number.
        :return: The sale.
        """
        # Create a new sale
        new_sale = Folder(quantity=quantity, total_price=total_price, item_id=item_id, item_name=item_name,
                          user_id=user_id, user_s_number=user_s_number)
        db.session.add(new_sale)
        db.session.commit()
        return new_sale

    @classmethod
    def update(cls, id: int, **kwargs) -> Sale:
        """
        Update this sale's data fields.

        :param id: The item ID of the sale to update.
        :param kwargs: The fields are updated with keyword arguments.
        :return: The updated sale.
        """
        modified_sale = Sale.query.get(id=id)

        # If no kwarg is given for an attribute, set it to the already stored attribute
        modified_sale.id = kwargs.get('id', modified_sale.id)
        modified_sale.quantity = kwargs.get('quantity', modified_sale.quantity)
        modified_sale.total_price = kwargs.get('total_price', modified_sale.total_price)
        modified_sale.item_id = kwargs.get('item_id', modified_sale.item_id)
        modified_sale.item_name = kwargs.get('item_name', modified_sale.item_name)
        modified_sale.user_id = kwargs.get('user_id', modified_sale.user_id)
        modified_sale.user_s_number = kwargs.get('user_s_number', modified_sale.user_s_number)
        modified_sale.api_id = kwargs.get('api_id', modified_sale.api_id)
        modified_sale.api_created = kwargs.get('api_created', modified_sale.api_created)
        modified_sale.status = kwargs.get('status', modified_sale.status)
        modified_sale.error_msg = kwargs.get('error_msg', modified_sale.error_msg)

        modified_sale.updated = datetime.now()
        db.session.commit()

        return modified_sale

    @classmethod
    def delete(cls, id: int) -> Sale:
        """
        Delete a sale.

        :param id: ID of the sale to delete.
        :return: The deleted sale.
        """
        deleted_sale = Sale.query.get(id=id)
        db.session.delete(deleted_sale)
        db.session.commit()

        return deleted_sale

    @classmethod
    def list_all(cls) -> list:
        """
        List all sales sorted by id.

        :return: A List of all sales.
        """
        # TODO: Add a way to sort result differently
        return Sale.query.order_by(asc(id=Sale.id)).all()

    @classmethod
    def get(cls, id: int) -> Sale:
        """
        Return the sale with that id.

        :param id: The id to get the sale by.
        :return: The sale.
        """
        return Sale.query.get(id=id)

    @classmethod
    def get_by_user_id(cls, user_id: int) -> list:
        """
        List all sales by this user.

        :return: A List of all sales by the yser.
        """
        # TODO: Add a way to sort result differently
        return Sale.query.filter_by(user_id=user_id).all()

    @classmethod
    def get_by_item_id(cls, item_id: int) -> list:
        """
        List all sales of this item.

        :return: A List of all sales by the item.
        """
        # TODO: Add a way to sort result differently
        return Sale.query.filter_by(item_id=item_id).all()

# class StreeplijstDBController(DBController):
#
#     @classmethod
#     def create_folder(cls, folder_id: int = None, mapping: dict = None, timeout: float = TIMEOUT,
#                       auto_commit=True) -> Folder:
#         """
#         Reads config.py and returns a single Folder object with the specified name.
#
#         :param folder_id: The folder id to read.
#         :param mapping: Optional dict which contains the folder meta values.
#         :param timeout: Timeout for the post request. Defaults to config.py TIMEOUT.
#         :param auto_commit: When set to True, commits the changes to the database at the end of the method call.
#         :return: The Folder object
#         """
#         if folder_id is not None:
#             folder_config = FOLDERS[folder_id]  # Load the folder configuration
#         elif mapping is not None:
#             folder_config = {'name': '', 'id': 1, 'media': '', }  # Set a default dict for the folder configuration
#             folder_config.update(mapping)  # Replace the default dict values with the passed in kwargs
#         else:
#             raise TypeError("create_folder expected at least a folder_id or a dictionary with mapping, got None.")
#         folder = Folder(folder_config['name'], folder_config['id'], folder_config['media'])  # Create Folder object
#         cls.add(folder, auto_commit=True)  # Add and commit the unfinished folder
#
#         # Populate the folder with items and commit to the database
#         cls.sync_folder(folder_id=folder.id, force_sync=True, timeout=timeout, auto_commit=auto_commit)
#         return folder  # Return the folder
#
#     @classmethod
#     def create_item(cls, item_id: int, timeout: float = TIMEOUT, auto_commit=True) -> Item:
#         """
#         Create an item from an API call.
#
#         :param item_id: Item ID
#         :param timeout: Timeout for the post request. Defaults to config.py TIMEOUT.
#         :param auto_commit: When set to True, commits the changes to the database at the end of the method call.
#         """
#         item_details = api.get_product(item_id=item_id, timeout=timeout)  # GET all item details from the API
#         item = Item(name=item_details['name'], id=item_details['id'], price=item_details['price'], folder=None,
#                     folder_id=item_details['folder_id'], published=item_details['published'],
#                     media=item_details['media'])
#         cls.add(item, auto_commit=auto_commit)  # Add the item to the database
#         return item  # Return the item
#
#     @classmethod
#     def create_sale(cls, item_id: int, user_id: int, quantity: int, auto_commit=True) -> Sale:
#         """
#         Create an item from an API call.
#
#         :param item_id: Item ID
#         :param user_id: User ID (not username)
#         :param quantity: Quantity of the item to buy
#         :param auto_commit: When set to True, commits the changes to the database at the end of the method call.
#         """
#         item = cls.get_item(item_id)  # Retrieve the item from the database
#         user = cls.get_user(user_id)  # Retrieve the user from the database
#
#         if not item or not user:  # If the item or the user do not exist in the database, return None
#             return None  # TODO: Change this exception
#
#         sale = Sale(user, item, quantity)  # Create the sale
#         cls.add(sale, auto_commit=auto_commit)  # Add the sale to the database
#         return sale  # Return the sale
#
#     # TODO: Add a post_sale method which also updates the database
#
#     @staticmethod
#     def get_item(item_id: int) -> Item:
#         """
#         Get an item from the database
#
#         :param item_id: Item ID
#         :return: The Item instance
#         """
#         return Item.query.filter_by(id=item_id).first()
#
#     @classmethod
#     def get_folder(cls, folder_id: int, sync: bool = False, force_sync: bool = True, update_interval=10,
#                    timeout: float = TIMEOUT, auto_commit: bool = False) -> Folder:
#         """
#         Return a folder from the database. If no folder was found, return None
#
#         :param folder_id: The folder to sync
#         :param sync: When set to True, the folder will be synced with the API before being returned.
#         :param force_sync: When set to True, the folder is synced with the API regardless of folder.last_synchronized.
#         :param update_interval: The time in minutes the folder should be out of sync before it is updated. If
#         datetime.now() - folder.last_synchronized > update_interval, the folder is synced with the API.
#         :param timeout: Timeout for the get request. Defaults to config.py TIMEOUT.
#         :param auto_commit: When set to True, commits the changes to the database at the end of the method call.
#         :return: The folder. If no folder was found, return None.
#         """
#         folder = Folder.query.filter_by(id=folder_id).first()
#         if folder:  # If a folder was found
#             if sync is True:  # If the folder should be synchronized with the API
#                 cls.sync_folder(folder.id, force_sync=force_sync, update_interval=update_interval, timeout=timeout,
#                                 auto_commit=auto_commit)
#         return folder
#
#     @classmethod
#     def get_or_create_folder(cls, folder_id: int = None, sync: bool = False, force_sync: bool = True,
#                              update_interval=10, timeout: float = TIMEOUT, auto_commit: bool = False) -> Folder:
#         """
#         Get the folder from the database, or create it if it does not exist in the database.
#
#         :param folder_id: Folder ID to retrieve
#         :param sync: When set to True, the folder will be synced with the API before being returned.
#         :param force_sync: When set to True, the folder is synced with the API regardless of folder.last_synchronized.
#         :param update_interval: The time in minutes the folder should be out of sync before it is updated. If
#         datetime.now() - folder.last_synchronized > update_interval, the folder is synced with the API.
#         :param timeout: Timeout for the get request. Defaults to config.py TIMEOUT.
#         :param auto_commit: When set to True, commits the changes to the database at the end of the method call.
#         :return: The folder.
#         """
#         folder = cls.get_folder(folder_id=folder_id, sync=sync, force_sync=force_sync, update_interval=update_interval,
#                                 timeout=timeout, auto_commit=False)
#         if not folder:
#             folder = cls.create_folder(folder_id=folder_id, timeout=timeout, auto_commit=False)
#
#         if auto_commit is True:
#             cls.commit()
#         return folder
#
#     @staticmethod
#     def get_sale(sale_id: int) -> Sale:
#         """
#         Return a sale from the database.
#
#         :param sale_id: Sale ID. This is the local ID.
#         :return: The Sale instance
#         """
#         # TODO: Be able to search for sales by date, item, user or api_id
#         return Sale.query.filter_by(id=sale_id).first()
#
#     @classmethod
#     def sync_folder(cls, folder_id, force_sync: bool = True, update_interval=10, timeout: float = TIMEOUT,
#                     auto_commit: bool = False) -> None:
#         """
#         GET all items from Congressus, update the folder.items list and return a dict of all items.
#
#         :param folder_id: The folder to sync
#         :param force_sync: When set to True, the folder is synced with the API regardless of folder.last_synchronized.
#         :param update_interval: The time in minutes the folder should be out of sync before it is updated. If
#         datetime.now() - folder.last_synchronized > update_interval, the folder is synced with the API.
#         :param timeout: Timeout for the get request. Defaults to config.py TIMEOUT.
#         :param auto_commit: When set to True, commits the changes to the database at the end of the method call.
#         """
#         folder = cls.get_folder(folder_id, sync=False)
#         if not folder:
#             return  # TODO: Put in a fitting FolderNotInDatabaseException
#
#         td = timedelta(minutes=update_interval)
#         if force_sync or (datetime.now() - folder.last_synchronized) > td:  # If the folder should update
#             items_list = api.get_products_in_folder(folder.id, timeout=timeout)  # get items in the folder from API
#             for item_dict in items_list:  # Iterate all items in the response
#                 item = folder.get_item(item_dict['id'])  # Get the item from the folder
#                 if not item:
#                     # If the item was not found in the folder, create a new one. It is linked with the folder upon
#                     # initialization.
#                     item = Item(name=item_dict['name'], id=item_dict['id'], price=item_dict['price'], folder=folder,
#                                 folder_id=item_dict['folder_id'], published=item_dict['published'],
#                                 media=item_dict['media'])
#                 else:  # If an item was found, update the item fields
#                     item.update(name=item_dict['name'], id=item_dict['id'], price=item_dict['price'], folder=folder,
#                                 folder_id=item_dict['folder_id'], published=item_dict['published'],
#                                 media=item_dict['media'])
#             folder.last_synchronized = datetime.now()  # Set the last updated time to now
#
#         if auto_commit is True:
#             cls.commit()

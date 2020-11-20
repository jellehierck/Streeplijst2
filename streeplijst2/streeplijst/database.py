from datetime import datetime, timedelta

from sqlalchemy import asc

from streeplijst2.streeplijst.models import Folder, Sale, Item
from streeplijst2.extensions import db
import streeplijst2.api as api

UPDATE_INTERVAL = 60 * 60 * 4  # Nr of seconds between automatic updates (default 4 hours)  # TODO: Add this to config


class FolderNotInDatabaseException(Exception):  # TODO: Add a streeplijst base exception module
    """Error when a folder could not be loaded from the database."""


class TotalPriceMismatchWarning(UserWarning):  # TODO: Add a streeplijst base warning module
    """Warning when the total price of the sale does not match between the locally stored value and the value returned
    by the API."""


class ItemDB:

    @classmethod
    def create(cls, id: int, name: str, price: int, published: bool, folder_id: int, folder_name: int,
               media: str = None, **kwargs) -> Item:
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
        modified_item = Item.query.get(id)

        # If no kwarg is given for an attribute, set it to the already stored attribute
        modified_item.name = kwargs.get('name', modified_item.name)
        modified_item.price = kwargs.get('price', modified_item.price)
        modified_item.published = kwargs.get('published', modified_item.published)
        modified_item.media = kwargs.get('media', modified_item.media)
        modified_item.folder_id = kwargs.get('folder_id', modified_item.folder_id)
        modified_item.folder_name = kwargs.get('folder_name', modified_item.folder_name)

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
        deleted_item = Item.query.get(id)
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
        return Item.query.order_by(asc(Item.id)).all()

    @classmethod
    def get(cls, id: int) -> Item:
        """
        Return the item with that id.

        :param id: The id to get the item by.
        :return: The item.
        """
        return Item.query.get(id)

    @classmethod
    def get_by_folder_id(cls, folder_id: int) -> list:
        """
        Return the items in the folder with that id.

        :param folder_id: The folder id to get items by.
        :return: A List of items.
        """
        return Item.query.filter_by(folder_id=folder_id).all()


class FolderDB:

    @classmethod
    def load_folder(cls, folder_id: int, force_sync: bool = False,
                    auto_sync_interval: float = UPDATE_INTERVAL, timeout: float = api.TIMEOUT) -> Folder:
        """
        Load a folder from the database or from the API. The database loads much faster but may be out of sync with the
        API.

        :param folder_id: Folder ID to retrieve.
        :param force_sync: When set to True, the folder will sync its contents with the API.
        :param auto_sync_interval: Alternative sync interval in seconds (defaults to cls.UPDATE_INTERVAL).
        :param timeout: Timeout for the API request in seconds (defautls to api.TIMEOUT).
        :return: The Folder instance.
        """
        folder = cls.get(folder_id)
        if folder is None:  # The folder was not in the database
            raise FolderNotInDatabaseException("Folder not in local database. Add it using FolderDB.create()")

        # Check if the folder contents should be updated.
        update_threshold = datetime.now() - timedelta(seconds=auto_sync_interval)
        if force_sync is True or folder.synchronized < update_threshold:  # The folder should sync with the API
            items = api.get_products_in_folder(folder.id, timeout=timeout)  # Make the api call
            for item_dict in items:  # Update existing items or create a new item if it did not exist in db before
                ItemDB.create(**item_dict)
            FolderDB.update(folder.id, synchronized=datetime.now())  # Update the timed folder fields.

        return folder

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
        modified_folder = Folder.query.get(id)

        # If no kwarg is given for an attribute, set it to the already stored attribute
        modified_folder.name = kwargs.get('name', modified_folder.name)
        modified_folder.media = kwargs.get('media', modified_folder.media)
        modified_folder.synchronized = kwargs.get('synchronized', modified_folder.synchronized)

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
        deleted_folder = Folder.query.get(id)
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
        return Folder.query.order_by(asc(Folder.id)).all()

    @classmethod
    def get(cls, id: int) -> Folder:
        """
        Return the folder with that id.

        :param id: The id to get the folder by.
        :return: The folder.
        """
        return Folder.query.get(id)

    @classmethod
    def get_items_in_folder(cls, id: int) -> list:
        """
        Get all items in a specific folder. This is synonymous to ItemController.get_by_folder_id().

        :param id: Folder id to get items for.
        :return: A list of all items in that folder.
        """
        return ItemDB.get_by_folder_id(id)


class SaleDB:

    @classmethod
    def post_sale(cls, id: int, timeout: float = api.TIMEOUT) -> Sale:
        """
        POST the sale to the API.

        :param id: The ID of the sale to post.
        :param timeout: Timeout for the API request in seconds (defautls to api.TIMEOUT).
        """
        sale = SaleDB.get(id)

        try:
            response = api.post_sale(user_id=sale.user_id, product_id=sale.item_id, quantity=sale.quantity,
                                     timeout=timeout)
            updated_sale = SaleDB.update(id=sale.id,
                                         api_id=response['id'],
                                         api_reference=response['reference'],
                                         api_created=response['created'],
                                         status=Sale.STATUS_OK)

            # Check the prices
            api_total_price = 0
            for item in response['items']:  # Adds prices of all items in sale to check
                api_total_price += item['total_price']  # Synchronize the total prize with API response

            if api_total_price != sale.total_price:  # Check if the total price matches
                raise TotalPriceMismatchWarning(
                    "total_price does not match. Local total_price: %d   API total_price: %d" % (
                        sale.total_price, api_total_price))

            return updated_sale

        except TotalPriceMismatchWarning as warn:  # If warning is raised, add message to the sale but continue normally
            updated_sale = SaleDB.update(id=sale.id,
                                         status=sale.STATUS_TOTAL_PRICE_MISMATCH,  # Store the warnning
                                         error_msg=str(warn))  # Store the warning message
            return updated_sale  # Return the sale

        except api.UserNotSignedException as err:  # The user needs to sign their SDD before posting sales
            SaleDB.update(id=sale.id,
                          status=Sale.STATUS_SDD_NOT_SIGNED,  # Store the reason the request failed
                          error_msg=str(err))  # Save the entire error message
            raise err

        except api.Timeout as err:  # If a Timeout error occurred
            SaleDB.update(id=sale.id,
                          status=Sale.STATUS_TIMEOUT,  # Store the reason the request failed
                          error_msg=str(err))  # Save the entire error message
            raise err

        except api.HTTPError as err:  # If an HTTPError occurred, the request was bad
            SaleDB.update(id=sale.id,
                          status=Sale.STATUS_HTTP_ERROR,  # Store the reason the request failed
                          error_msg=str(err))  # Save the entire error message
            raise err

        except Exception as err:  # If another error occurred, something else went wrong
            SaleDB.update(id=sale.id,
                          status=Sale.STATUS_UNKNOWN_ERROR,  # Store the reason the request failed
                          error_msg=str(err))  # Save the entire error message
            raise err

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
        new_sale = Sale(quantity=quantity, total_price=total_price, item_id=item_id, item_name=item_name,
                        user_id=user_id, user_s_number=user_s_number)
        db.session.add(new_sale)
        db.session.commit()
        return new_sale

    @classmethod
    def update(cls, id: int, **kwargs) -> Sale:
        """
        Update this sale's data fields.

        :param id: The ID of the sale to update.
        :param kwargs: The fields are updated with keyword arguments.
        :return: The updated sale.
        """
        modified_sale = Sale.query.get(id)

        # If no kwarg is given for an attribute, set it to the already stored attribute
        modified_sale.quantity = kwargs.get('quantity', modified_sale.quantity)
        modified_sale.total_price = kwargs.get('total_price', modified_sale.total_price)
        modified_sale.item_id = kwargs.get('item_id', modified_sale.item_id)
        modified_sale.item_name = kwargs.get('item_name', modified_sale.item_name)
        modified_sale.user_id = kwargs.get('user_id', modified_sale.user_id)
        modified_sale.user_s_number = kwargs.get('user_s_number', modified_sale.user_s_number)

        modified_sale.api_id = kwargs.get('api_id', modified_sale.api_id)
        modified_sale.api_reference = kwargs.get('api_reference', modified_sale.api_reference)
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
        deleted_sale = Sale.query.get(id)
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
        return Sale.query.order_by(asc(Sale.id)).all()

    @classmethod
    def get(cls, id: int) -> Sale:
        """
        Return the sale with that id.

        :param id: The id to get the sale by.
        :return: The sale.
        """
        return Sale.query.get(id)

    @classmethod
    def get_by_user_id(cls, user_id: int) -> list:
        """
        List all sales by this user.

        :return: A List of all sales by the user.
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

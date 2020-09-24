from datetime import datetime
from requests.exceptions import HTTPError, Timeout

from streeplijst2.config import TIMEOUT
from streeplijst2.models import User
from streeplijst2.extensions import db
import streeplijst2.api as api


# class DBBase(db.Model):
#     # TODO: add a base class here
#     id = None
#     last_updated = None
#     created = None
#
#     def update(self):
#         pass


class Folder(db.Model):
    # Class attributes for SQLAlchemy
    __tablename__ = 'folder'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    media = db.Column(db.String)
    last_synchronized = db.Column(db.DateTime)  # The folder has not been updated upon initialization

    def __init__(self, name: str, id: int, media: str = ''):
        """
        Instantiates a Folder object.

        :param name: Folder name
        :param id: Folder id
        :param media: (optional) Image URL
        """
        self.name = name
        self.id = id
        self.media = media
        self.items = []  # There are no items in the non-synchronized folder
        self.last_synchronized = datetime.min  # The folder has not been synchronized upon initialization

    def get_item(self, item_id):
        """
        Get an item instance in this folder.

        :param item_id: The item ID to retrieve.
        :return: An Item instance.
        """
        for item in self.items:
            if item.id == item_id:
                return item
        return None

    def update(self, **kwargs):
        """
        Update this folder's meta fields.

        :param kwargs: The fields are updated with keyword arguments.
        """
        # If no kwarg is given for an attribute, set it to the already stored attribute
        self.id = kwargs.get('id', self.id)
        self.name = kwargs.get('name', self.name)
        self.media = kwargs.get('media', self.media)
        # self.items = kwargs.get('items', self.items)  # The items cannot be updated, they need to be synced with API
        self.last_synchronized = kwargs.get('last_synchronized', self.last_synchronized)


class Item(db.Model):
    # Class attributes for SQLAlchemy
    __tablename__ = 'items'

    # Table columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    price = db.Column(db.Integer)
    published = db.Column(db.Boolean)
    media = db.Column(db.String)
    folder_id = db.Column(db.Integer, db.ForeignKey(Folder.__tablename__ + '.id'))  # Add a link to the folder id
    folder = db.relationship(Folder,  # Add a column to the folder table which links to the items in that folder
                             backref=__tablename__,  # Link back to the items from the folders table
                             lazy=True,  # Data is only loaded as necessary
                             )

    def __init__(self, name: str, id: int, price: int, folder: Folder, folder_id: int, published: bool, media: str):
        """
        Instantiate an Item object. This Item contains all relevant information provided by the API response.

        :param name: Item name
        :param id: Item id
        :param price: Item price in cents
        :param folder: Folder instance
        :param folder_id: Folder id
        :param published: True if the item is published, false otherwise
        :param media: (optional) Image URL
        """
        self.name = name
        self.id = id
        self.price = int(price)
        self.folder = folder
        self.folder_id = folder_id
        self.published = published
        self.media = media

    def update(self, **kwargs):
        """
        Update this item's data fields.

        :param kwargs: The fields are updated with keyword arguments.
        """
        # If no kwarg is given for an attribute, set it to the already stored attribute
        self.name = kwargs.get('name', self.name)
        self.id = kwargs.get('id', self.id)
        self.price = kwargs.get('price', self.price)
        self.folder = kwargs.get('folder', self.folder)
        self.folder_id = kwargs.get('folder_id', self.folder_id)
        self.published = kwargs.get('published', self.published)
        self.media = kwargs.get('media', self.media)


class Sale(db.Model):
    # Class attributes for SQLAlchemy
    __tablename__ = 'sale'

    # Table columns
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Store sales with a local ID
    quantity = db.Column(db.Integer)  # Quantity of item purchased
    total_price = db.Column(db.Integer)  # Total price of the sale (quantity * item.price) in cents
    item_name = db.Column(db.String, db.ForeignKey(Item.__tablename__ + '.name'))  # Add a link to the item name
    item = db.relationship(Item,  # Add a column to the item table which links to the sales for that item
                           backref=__tablename__,  # Link back to the sales from the item table
                           lazy=True)  # Data is only loaded as necessary

    user_s_number = db.Column(db.String, db.ForeignKey(User.__tablename__ + '.s_number'))  # Add a link to the folder id
    user = db.relationship(User,  # Add a column to the user table which links to the sales for that user
                           backref=__tablename__,  # Link back to the sales from the user table
                           lazy=True)  # Data is only loaded as necessary

    api_id = db.Column(db.Integer)  # Congressus ID
    # TODO: Change local_id and id to work with DBBase class (probably use self.id for both Congressus and internal id
    #  and dropping self.local_id)
    status = db.Column(db.String)
    created = db.Column(db.DateTime)  # Created date
    error_msg = db.Column(db.String)

    def __init__(self, user: User, item: Item, quantity: int):
        """
        Instantiates a Sale object.

        :param user: User object
        :param item: Item object
        :param quantity: Amount of the item to buy
        """
        self.user = user
        self.item = item
        self.quantity = quantity
        self.total_price = quantity * self.item.price  # The total price is set
        self.api_id = None  # The congressus id for this sale
        self.created = None  # The datetime this sale was created and posted
        self.status = None  # The status of the API response  # TODO: add a payment type in the future

    def post_sale(self, timeout: float = TIMEOUT) -> dict:
        """
        POST the sale to Congressus.

        :param timeout: Timeout for the post request. Defaults to config.py TIMEOUT.
        """
        user_id = self.user.id
        product_id = self.item.id
        try:
            response = api.post_sale(user_id, product_id, self.quantity, timeout=timeout)
            for item in response['items']: # Adds prices of multiple items. Usually there will only be one item per sale
                self.total_price += int(item['total_price'])  # Synchronize the total prize with API response
            self.api_id = int(response['id'])
            self.created = datetime.fromisoformat(response['created'])
            self.status = 'OK'
            return response

        except Timeout as err:  # If an Timeout error occurred
            self.api_id = 0  # Set the congressus ID to 0 to indicate a failed sale
            self.status = 'TIMEOUT'  # Store the reason the request failed
            self.created = datetime.now()  # Store the current time
            self.error_msg = str(err)  # Save the entire error message
            raise

        except HTTPError as err:  # If an HTTPError occurred, the request was bad
            self.api_id = 0  # Set the congressus ID to 0 to indicate a bad sale
            self.status = err.response.reason  # Store the reason the request failed
            self.created = datetime.now()  # Store the current time
            self.error_msg = str(err)  # Save the entire error message
            raise

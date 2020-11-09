from datetime import datetime
from requests.exceptions import HTTPError, Timeout

from streeplijst2.config import TIMEOUT
from streeplijst2.models import User
from streeplijst2.extensions import db
import streeplijst2.api as api


class Folder(db.Model):
    # Class attributes for SQLAlchemy
    __tablename__ = 'folders'

    # Table columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    media = db.Column(db.String, nullable=True)
    synchronized = db.Column(db.DateTime)  # When was this folder last synchronized with the API

    created = db.Column(db.DateTime)
    updated = db.Column(db.DateTime)

    def __init__(self, **kwargs):
        """
        Instantiates a Folder object.

        :param name: Folder name.
        :param id: Folder id.
        :param media: (optional) Image URL.
        """
        super().__init__(**kwargs)
        self.created = datetime.now()
        self.updated = datetime.now()
        self.synchronized = datetime.min  # Set initial synchronized date very far in the past to force synchronization


class Item(db.Model):
    # Class attributes for SQLAlchemy
    __tablename__ = 'items'

    # Table columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    price = db.Column(db.Integer)
    published = db.Column(db.Boolean)
    media = db.Column(db.String, nullable=True)
    folder_id = db.Column(db.Integer, db.ForeignKey(Folder.__tablename__ + '.id'))  # Add a link to the folder id
    folder_name = db.Column(db.String, db.ForeignKey(Folder.__tablename__ + '.name'))  # Add a link to the folder name

    created = db.Column(db.DateTime)
    updated = db.Column(db.DateTime)

    def __init__(self, **kwargs):
        """
        Instantiate an Item object. This Item contains only relevant information provided by the API response.

        :param name: Item name.
        :param id: Item id.
        :param price: Item price in cents.
        :param folder_id: Folder id.
        :param folder_name: Folder name.
        :param published: True if the item is published, False otherwise.
        :param media: (optional) Image URL.
        """
        super().__init__(**kwargs)
        self.created = datetime.now()
        self.updated = datetime.now()


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

    created = db.Column(db.DateTime)
    last_updated = db.Column(db.DateTime)

    api_id = db.Column(db.Integer)  # Congressus ID
    api_created = db.Column(db.DateTime)  # Created according to the API
    status = db.Column(db.String)
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
        self.created = datetime.now()
        self.last_updated = datetime.now()
        self.api_id = None  # The congressus id for this sale
        self.api_created = None  # The datetime this sale was created and posted
        self.status = None  # The status of the API response  # TODO: add a payment type in the future

    def post_sale(self, timeout: float = TIMEOUT) -> dict:
        """
        POST the sale to Congressus.

        :param timeout: Timeout for the post request. Defaults to config.py TIMEOUT.
        """
        user_id = self.user.id
        product_id = self.item.id

        self.last_updated = datetime.now()

        try:
            response = api.post_sale(user_id, product_id, self.quantity, timeout=timeout)
            for item in response[
                'items']:  # Adds prices of multiple items. Usually there will only be one item per sale
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

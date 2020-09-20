from datetime import datetime
from requests.exceptions import HTTPError, Timeout

from streeplijst2.config import TIMEOUT
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
        Update this folder's data fields using the fields from another folder. NOTE: self.items cannot be updated with
        this method, synchronize the folder with the API instead.

        :param folder: A Folder object with the up-to-date data.
        """
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
        # If no item was given, update any new fields from the kwargs. If no kwarg is given for an attribute, set it
        # to the already stored attribute
        self.name = kwargs.get('name', self.name)
        self.id = kwargs.get('id', self.id)
        self.price = kwargs.get('price', self.price)
        self.folder = kwargs.get('folder', self.folder)
        self.folder_id = kwargs.get('folder_id', self.folder_id)
        self.published = kwargs.get('published', self.published)
        self.media = kwargs.get('media', self.media)


class User(db.Model):
    # Class attributes for SQLAlchemy
    __tablename__ = 'user'

    # Table columns
    id = db.Column(db.Integer, primary_key=True)
    s_number = db.Column(db.String)
    first_name = db.Column(db.String)
    last_name_prefix = db.Column(db.String)
    last_name = db.Column(db.String)
    date_of_birth = db.Column(db.DateTime)
    has_sdd_mandate = db.Column(db.Boolean)
    profile_picture = db.Column(db.String)

    def __init__(self, s_number: str, id: int, date_of_birth: datetime, first_name: str, last_name: str,
                 last_name_prefix: str = '', has_sdd_mandate: bool = False, profile_picture: dict = ''):
        """
        Create a new User object.

        :param s_number: Student or Employee number (Congressus user name)
        :param id: Congressus user id
        :param date_of_birth: Date of Birth (ISO formatted datetime string)
        :param first_name: First Name
        :param last_name: Last Name
        :param last_name_prefix: Last Name Prefix
        :param has_sdd_mandate: Has this user signed their SDD mandate
        :param profile_picture: Dict with URL strings to profile pictures
        """
        self.s_number = s_number
        self.id = id
        self.first_name = first_name
        self.last_name_prefix = last_name_prefix
        self.last_name = last_name
        self.date_of_birth = date_of_birth
        self.has_sdd_mandate = has_sdd_mandate
        self.profile_picture = profile_picture

    def update(self, **kwargs):
        """
        Update this user's data fields.

        :param kwargs: The fields are updated with keyword arguments.
        """
        # If no item was given, update any new fields from the kwargs. If no kwarg is given for an attribute, set it
        # to the already stored attribute
        self.s_number = kwargs.get('s_number', self.s_number)
        self.id = kwargs.get('id', self.id)
        self.first_name = kwargs.get('first_name', self.first_name)
        self.last_name_prefix = kwargs.get('last_name_prefix', self.last_name_prefix)
        self.last_name = kwargs.get('last_name', self.last_name)
        self.date_of_birth = kwargs.get('date_of_birth', self.date_of_birth)
        self.has_sdd_mandate = kwargs.get('has_sdd_mandate', self.has_sdd_mandate)
        self.profile_picture = kwargs.get('profile_picture', self.profile_picture)


class Sale(db.Model):
    # Class attributes for SQLAlchemy
    __tablename__ = 'sale'

    # Table columns
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Store sales with a local ID
    api_id = db.Column(db.Integer)  # Congressus ID
    # TODO: Change local_id and id to work with DBBase class (probably use self.id for both Congressus and internal id
    #  and dropping self.local_id)
    status = db.Column(db.String)
    created = db.Column(db.DateTime)  # Created date
    quantity = db.Column(db.Integer)  # Quantity of item purchased
    item_name = db.Column(db.String, db.ForeignKey(Item.__tablename__ + '.name'))  # Add a link to the item name
    item = db.relationship(Item,  # Add a column to the item table which links to the sales for that item
                           backref=__tablename__,  # Link back to the sales from the item table
                           lazy=True)  # Data is only loaded as necessary

    user_s_number = db.Column(db.String, db.ForeignKey(User.__tablename__ + '.s_number'))  # Add a link to the folder id
    user = db.relationship(User,  # Add a column to the user table which links to the sales for that user
                           backref=__tablename__,  # Link back to the sales from the user table
                           lazy=True)  # Data is only loaded as necessary

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
        self.api_id = None  # The congressus id for this sale
        self.created = None  # The datetime this sale was created and posted
        self.status = None  # The status of the API response  # TODO: add a payment type in the future

    def post_sale(self, timeout: float = TIMEOUT):
        """
        POST the sale to Congressus.

        :param timeout: Timeout for the post request. Defaults to config.py TIMEOUT.
        """
        user_id = self.user.id
        product_id = self.item.id
        try:
            response = api.post_sale(user_id, product_id, self.quantity, timeout=timeout)
            self.api_id = response['id']
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

from datetime import datetime
from requests.exceptions import HTTPError, Timeout

from streeplijst2.database import db
from streeplijst2.config import FOLDERS, TIMEOUT
import streeplijst2.api as api


class Folder(db.Model):
    # Class attributes for SQLAlchemy
    __tablename__ = 'folder'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    media = db.Column(db.String)
    last_updated = db.Column(db.DateTime)  # The folder has not been updated upon initialization

    @classmethod
    def from_mapping(cls, mapping: dict = None, timeout: float = TIMEOUT):
        """
        Create a folder from passing in a custom mapping.
        :param mapping: dict with keys 'name', 'id' and 'media'
        :param timeout: Timeout for the post request. Defaults to config.py TIMEOUT.
        :return: The Folder object
        """
        folder_config = {  # Set a default dict for the folder configuration passed in
                'name': '',
                'id': 1,
                'media': '',
        }
        folder_config.update(mapping)  # Replace the default dict values with the passed in kwargs

        folder = Folder(folder_config['name'], folder_config['id'], folder_config['media'])  # Create Folder object
        folder.update_items(timeout=timeout)  # Load all items from the API
        return folder

    @classmethod
    def all_folders_from_config(cls, timeout: float = TIMEOUT):
        """
        Reads all folders in config.py and returns a dict of Folder objects. This call might take several seconds to
        complete.

        :param timeout: Timeout for the post request. Defaults to config.py TIMEOUT. Note: this timeout is considered
        per folder requested. Calling two folders could result in a maximum waiting time of two times timeout seconds.
        per
        :return: A dict with keys as folder_id and value as Folder
        """
        result = dict()
        for folder_name in FOLDERS:  # Iterate all items in folder configuration
            folder = cls.from_config(folder_name, timeout=timeout)  # Create Folder object
            result[folder.id] = folder  # Store folder object
        return result

    @classmethod
    def from_config(cls, folder_name: str, timeout: float = TIMEOUT):
        """
        Reads config.py and returns a single Folder object with the specified name.

        :param folder_name: The folder name to read.
        :param timeout: Timeout for the post request. Defaults to config.py TIMEOUT.
        :return: The Folder object
        """
        folder_config = FOLDERS[folder_name]  # Load the folder configuration
        folder = Folder(folder_config['name'], folder_config['id'], folder_config['media'])  # Create Folder object
        folder.update_items(timeout=timeout)  # Load all items from the API
        return folder

    def __init__(self, name: str, id: int, media: str = '', items: dict = None):
        """
        Instantiates a Folder object.

        :param name: Folder name
        :param id: Folder id
        :param media: (optional) Image URL
        """
        self.name = name
        self.id = id
        self.media = media
        self.items = items
        self.last_updated = None  # The folder has not been updated upon initialization

    def update_items(self, timeout: float = TIMEOUT) -> dict:
        """
        GET all items from Congressus, update the self.items list and return a dict of all items.

        :param timeout: Timeout for the get request. Defaults to config.py TIMEOUT.
        :return: A dict with keys as item_id and values as Item
        """
        items_list = api.get_products_in_folder(self.id, timeout=timeout)  # get items in the folder from API
        result = dict()  # Empty dict to store items in
        for item_dict in items_list:  # Iterate all items in the response
            # result[item_dict["id"]] = Item(item_dict["name"], item_dict["id"], item_dict["price"],
            #                                item_dict["folder"], item_dict["folder_id"], item_dict["published"],
            #                                item_dict["media"])  # Create Item object
            result[item_dict['id']] = Item(name=item_dict['name'], id=item_dict['id'], price=item_dict['price'],
                                           folder=self, folder_id=item_dict['folder_id'],
                                           published=item_dict['published'], media=item_dict['media'])
        self.items = result  # Store the items in this folder instance
        self.last_updated = datetime.now()  # Set the last updated time to now
        return result


class Item(db.Model):
    # Class attributes for SQLAlchemy
    __tablename__ = 'item'

    # Table columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    price = db.Column(db.Float)
    published = db.Column(db.Boolean)
    media = db.Column(db.String)
    folder_id = db.Column(db.Integer, db.ForeignKey(Folder.__tablename__ + '.id'))  # Add a link to the folder id
    folder = db.relationship(Folder,  # Add a column to the folder table which links to the items in that folder
                             backref=__tablename__,  # Link back to the items from the folders table
                             lazy=True)  # Data is only loaded as necessary

    def __init__(self, name: str, id: int, price: float, folder: Folder, folder_id: int, published: bool,
                 media: list = None):
        """
        Instantiate an Item object. This Item contains all relevant information provided by the API response.

        :param name: Item name
        :param id: Item id
        :param price: Item price
        :param folder: Folder instance
        :param folder_id: Folder id
        :param published: True if the item is published, false otherwise
        :param media: (optional) Image URL
        """
        self.name = name
        self.id = id
        self.price = price
        self.folder = folder
        self.folder_id = folder_id
        self.published = published
        if not media:  # Store an image URL if the item has one.
            self.media = ''
        else:
            self.media = media[0]['url']


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

    @classmethod
    def from_api(cls, s_number: str, timeout: float = TIMEOUT):
        """
        Create a user from an API call.

        :param timeout: Timeout for the post request. Defaults to config.py TIMEOUT.
        :param s_number: Student or Employee number (Congressus user name)
        """
        user_details = api.get_user(s_number, timeout=timeout)  # GET all user details from the API
        user = cls(s_number, id=user_details['id'], date_of_birth=user_details['date_of_birth'],
                   first_name=user_details['first_name'], last_name=user_details['primary_last_name_main'],
                   last_name_prefix=user_details['primary_last_name_prefix'],
                   has_sdd_mandate=user_details['has_sdd_mandate'], profile_picture=user_details['profile_picture'])
        return user

    @classmethod
    def add_or_update_user(cls, user):
        """
        Add a user to the connected database. If a user with that congressus ID (user.id) already exists, update their
        information.

        :param user: The user to add to or update in the database
        """
        existing_user = cls.query.filter_by(id=user.id).first()  # Get the user as stored in the local db
        if existing_user:  # If the user was found in the local database
            existing_user._update(user)  # Set the local database user to the new user, updating any outdated fields
        else:  # If the user ws not found in the local database, create the user
            db.session.add(user)  # Add the user to the local database
        db.session.commit()  # Commit the changes to the database

    def __init__(self, s_number: str, id: int, date_of_birth: str, first_name: str, last_name: str,
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
        self.date_of_birth = datetime.fromisoformat(date_of_birth)
        self.has_sdd_mandate = has_sdd_mandate

        if not profile_picture:  # Store a profile picture URL if the user has one.
            self.profile_picture = ''
        else:
            self.profile_picture = profile_picture['url']

    def _update(self, user):
        """
        Update this user's data fields using the fields from another user.
        :param user: a User object with the up-to-date data.
        """
        self.s_number = user.s_number
        self.id = user.id
        self.first_name = user.first_name
        self.last_name_prefix = user.last_name_prefix
        self.last_name = user.last_name
        self.date_of_birth = user.date_of_birth
        self.has_sdd_mandate = user.has_sdd_mandate
        self.profile_picture = user.profile_picture


class Sale(db.Model):
    # Class attributes for SQLAlchemy
    __tablename__ = 'sale'

    # Table columns
    local_id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Store sales with a local ID
    id = db.Column(db.Integer)  # Congressus ID
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
        self.id = None  # The congressus id for this sale
        self.created = None  # The datetime this sale was created and posted
        self.status = None  # The status of the API response
        # TODO: add a payment type in the future

    def post_sale(self, timeout: float = TIMEOUT):
        """
        POST the sale to Congressus.

        :param timeout: Timeout for the post request. Defaults to config.py TIMEOUT.
        """
        user_id = self.user.id
        product_id = self.item.id
        try:
            response = api.post_sale(user_id, product_id, self.quantity, timeout=timeout)
            self.id = response['id']
            self.created = datetime.fromisoformat(response['created'])
            self.status = 'OK'
            return response

        except Timeout as err:  # If an Timeout error occurred
            self.id = 0  # Set the congressus ID to 0 to indicate a failed sale
            self.status = 'TIMEOUT'  # Store the reason the request failed
            self.created = datetime.now()  # Store the current time
            self.error_msg = str(err)  # Save the entire error message
            raise

        except HTTPError as err:  # If an HTTPError occurred, the request was bad
            self.id = 0  # Set the congressus ID to 0 to indicate a bad sale
            self.status = err.response.reason  # Store the reason the request failed
            self.created = datetime.now()  # Store the current time
            self.error_msg = str(err)  # Save the entire error message
            raise

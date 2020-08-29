from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship, backref
from requests.exceptions import HTTPError

from streeplijst2.database import Base
from streeplijst2.config import FOLDERS
import streeplijst2.api as api


class Folder(Base):
    # Class attributes for SQLAlchemy
    __tablename__ = 'folder'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    media = Column(String)
    last_updated = Column(DateTime)  # The folder has not been updated upon initialization

    @classmethod
    def all_folders_from_config(cls):
        """
        Reads all folders in config.py and returns a dict of Folder objects

        :return: A dict with keys as folder_id and value as Folder
        """
        result = dict()
        for folder_name in FOLDERS:  # Iterate all items in folder configuration
            folder = cls.from_config(folder_name)  # Create Folder object
            result[folder.id] = folder  # Store folder object
        return result

    @classmethod
    def from_config(cls, folder_name: str):
        """
        Reads config.py and returns a single Folder object with the specified name.

        :param folder_name: The folder name to read.
        :return: The Folder object
        """
        folder_config = FOLDERS[folder_name]  # Load the folder configuration
        folder = Folder(folder_config["name"], folder_config["id"], folder_config["media"])  # Create Folder object
        folder.update_items()  # Load all items from the API
        return folder

    def __init__(self, name: str, id: int, media: str = "", items: dict = None):
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

    def update_items(self) -> dict:
        """
        GET all items from Congressus, update the self.items list and return a dict of all items.

        :return: A dict with keys as item_id and values as Item
        """
        items_list = api.get_products_in_folder(self.id)  # Make the API call to get items in the folder
        result = dict()  # Empty dict to store items in
        for item_dict in items_list:  # Iterate all items in the response
            # result[item_dict["id"]] = Item(item_dict["name"], item_dict["id"], item_dict["price"],
            #                                item_dict["folder"], item_dict["folder_id"], item_dict["published"],
            #                                item_dict["media"])  # Create Item object
            result[item_dict["id"]] = Item(name=item_dict["name"], id=item_dict["id"], price=item_dict["price"],
                                           folder=self, folder_id=item_dict["folder_id"],
                                           published=item_dict["published"], media=item_dict["media"])
        self.items = result  # Store the items in this folder instance
        self.last_updated = datetime.now()  # Set the last updated time to now
        return result


class Item(Base):
    # Class attributes for SQLAlchemy
    __tablename__ = 'item'

    # Table columns
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Float)
    published = Column(Boolean)
    media = Column(String)
    folder_id = Column(Integer, ForeignKey(Folder.__tablename__ + '.id'))  # Add a link to the folder id
    folder = relationship(Folder,  # Add a column to the folder table which links to the items in that folder
                          backref=backref(__tablename__,  # Link back to the items from the folders table
                                          uselist=True,  # Load the items as a list in the folders table
                                          cascade='delete,all'))  # If the folder is deleted, also delete items

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
        if media is None:
            media = []
        self.name = name
        self.id = id
        self.price = price
        self.folder = folder
        self.folder_id = folder_id
        self.published = published
        if not media:  # Store an image URL if the item has one.
            self.media = ""
        else:
            self.media = media[0]['url']


class User(Base):
    # Class attributes for SQLAlchemy
    __tablename__ = 'user'

    # Table columns
    id = Column(Integer, primary_key=True)
    s_number = Column(String)
    first_name = Column(String)
    last_name_prefix = Column(String)
    last_name = Column(String)
    date_of_birth = Column(DateTime)
    has_sdd_mandate = Column(Boolean)
    profile_picture = Column(String)

    @classmethod
    def from_api(cls, s_number: str):
        """
        Create a user from an API call.

        :param s_number: Student or Employee number (Congressus user name)
        """
        user_details = api.get_user(s_number)  # GET all user details from the API and store relevant details
        user = cls(s_number, id=user_details['id'], date_of_birth=user_details['date_of_birth'],
                   first_name=user_details['first_name'], last_name=user_details['primary_last_name_main'],
                   last_name_prefix=user_details['primary_last_name_prefix'],
                   has_sdd_mandate=user_details['has_sdd_mandate'], profile_picture=user_details['profile_picture'])
        return user

    def __init__(self, s_number: str, id: int, date_of_birth: str, first_name: str, last_name: str,
                 last_name_prefix: str = "", has_sdd_mandate: bool = False, profile_picture: dict = ""):
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
            self.profile_picture = ""
        else:
            self.profile_picture = profile_picture['url']


class Sale(Base):
    # Class attributes for SQLAlchemy
    __tablename__ = 'sale'

    # Table columns
    internal_id = Column(Integer, primary_key=True, autoincrement=True)  # Store sales with an internal ID
    id = Column(Integer)  # Congressus ID
    created = Column(DateTime)  # Created date
    quantity = Column(Integer)  # Quantity of item purchased
    item_name = Column(String, ForeignKey(Item.__tablename__ + '.name'))  # Add a link to the item name
    item = relationship(Item,  # Add a column to the item table which links to the sales for that item
                        backref=backref(__tablename__,  # Link back to the sales from the item table
                                        uselist=True))  # Load the sales as a list in the item table

    user_s_number = Column(String, ForeignKey(User.__tablename__ + '.s_number'))  # Add a link to the folder id
    user = relationship(User,  # Add a column to the user table which links to the sales for that user
                        backref=backref(__tablename__,  # Link back to the sales from the user table
                                        uselist=True))  # Load the sales as a list in the user table

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

    def post_sale(self):
        """
        POST the sale to Congressus.
        """
        user_id = self.user.id
        product_id = self.item.id
        try:
            response = api.post_sale(user_id, product_id, self.quantity)
            self.id = response['id']
            self.created = datetime.fromisoformat(response['created'])
            self.status = 'OK'
            return response

        except HTTPError as e:  # If an HTTPError occurred, the request was bad
            self.id = 0  # Set the congressus ID to 0 to indicate a bad sale
            self.status = e.response.reason  # Store the reason the request failed
            self.created = datetime.now()  # Store the current time
            raise

import datetime

from streeplijst2.config import FOLDERS
import streeplijst2.api as api


def get_folder_from_config(folder_name):
    """
    Reads config.py and returns the Folder object with the specified name.

    :param folder_name: The folder name to read.
    :return: The Folder object
    """
    folder_config = FOLDERS[folder_name]  # Load the folder configuration
    folder = Folder(folder_config["name"], folder_config["id"], folder_config["media"])  # Create Folder object
    return folder


def get_all_folders_from_config():
    """
    Reads all folders in config.py and returns a dict of Folder objects

    :return: A dict with (key: value) (folder_id: Folder)
    """
    result = dict()
    for folder_name in FOLDERS:  # Iterate all items in folder configuration
        folder = get_folder_from_config(folder_name)  # Create Folder object
        result[folder.id] = folder  # Store folder object
    return result


class Folder:
    def __init__(self, name, id, media=""):
        """
        Instantiates a Folder object.

        :param name: Folder name
        :param id: Folder id
        :param media: (optional) Image URL
        """
        self.name = name
        self.id = id
        self.media = media
        self.last_updated = datetime.datetime.now().isoformat()  # Set the last updated time to now
        self.items = self.get_items()

    def get_items(self):
        """
        GET all items from API.

        :return: A dict with (key: value) (item_id: GetItem)
        """
        items_list = api.get_products_in_folder(self.id)  # Make the API call to get items in the folder
        result = dict()  # Empty dict to store items in
        for item_dict in items_list:  # Iterate all items in the response
            result[item_dict["id"]] = Item(item_dict["name"], item_dict["id"], item_dict["price"],
                                           item_dict["folder"], item_dict["folder_id"], item_dict["published"],
                                           item_dict["media"])  # Create GetItem object
        self.last_updated = datetime.datetime.now().isoformat()  # Set the last updated time to now
        return result


class Item:
    def __init__(self, name, id, price, folder, folder_id, published, media=""):
        """
        Instantiate an Item object. This Item contains all relevant information provided by the API response.

        :param name: Item name
        :param id: Item id
        :param price: Item price
        :param folder: Folder
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
        self.media = media


class User:

    @classmethod
    def from_api(cls, s_number: str) -> object:
        """
        Create a user from an API call.

        :param s_number: Student or Employee number (Congressus user name)
        """
        user_details = api.get_user(s_number)  # GET all user details from the API and store relevant details
        user = cls(s_number, user_id=user_details['id'], date_of_birth=user_details['date_of_birth'],
                   first_name=user_details['first_name'], last_name=user_details['primary_last_name_main'],
                   last_name_prefix=user_details['primary_last_name_prefix'],
                   has_sdd_mandate=user_details['has_sdd_mandate'], profile_picture=user_details['profile_picture'])
        return user

    def __init__(self, s_number: str, user_id: int, date_of_birth: str, first_name: str, last_name: str,
                 last_name_prefix: str = "",
                 has_sdd_mandate: bool = False, profile_picture: dict = ""):
        """
        Create a new User object.

        :param s_number: Student or Employee number (Congressus user name)
        :param user_id: Congressus user id
        :param date_of_birth: Date of Birth
        :param first_name: First Name
        :param last_name: Last Name
        :param last_name_prefix: Last Name Prefix
        :param has_sdd_mandate: Has this user signed their SDD mandate
        :param profile_picture: Dict with URL strings to profile pictures
        """
        self.s_number = s_number
        self.user_id = user_id
        self.first_name = first_name
        self.last_name_prefix = last_name_prefix
        self.last_name = last_name
        self.date_of_birth = date_of_birth
        self.has_sdd_mandate = has_sdd_mandate

        if profile_picture is None:  # Store a profile picture URL if the user has one.
            self.profile_picture = ""
        else:
            self.profile_picture = profile_picture['url_md']


class Sale:
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

    def post_sale(self):
        """
        POST the sale to Congressus.
        """
        user_id = self.user.user_id
        product_id = self.item.id
        api.post_sale(user_id, product_id, self.quantity)

import datetime

from streeplijst.config import FOLDERS
import streeplijst.api as api


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


class Sale:
    def __init__(self, user, item, quantity):
        """
        Instantiates a Sale object.
        :param user: User object
        :param item: Item object
        :param quantity: Amount of the item to buy
        """
        self.user = user
        self.item = item
        self.quantity = quantity

        self.user_id = user.user_id  # Store the user id for API call
        self.product_id = item.id  # Store the product ID for API call

    def submit_sale(self):
        api.post_sale(self.user_id, self.product_id, self.quantity)

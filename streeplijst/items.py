import datetime

from streeplijst.config import FOLDERS
import streeplijst.api as api


def get_folder_from_config(folder_name):
    """
    Reads the config.py file and returns the Folder object with that name.

    :param folder_name: The folder name to read.
    :return: The Folder object
    """
    folder_dict = FOLDERS[folder_name]  # Load the folder configuration
    folder = Folder(folder_dict["name"], folder_dict["id"], folder_dict["media"])  # Create Folder object
    return folder


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

        :return: A dict with (key: value) (item id: GetItem object)
        """
        items_list = api.get_products_in_folder(self.id)  # Make the API call to get items in the folder
        result = dict()  # Empty dict to store items in
        for item_dict in items_list:  # Iterate all items in the response
            result[item_dict["id"]] = GetItem(item_dict["name"], item_dict["id"], item_dict["price"],
                                              item_dict["folder"], item_dict["folder_id"], item_dict["published"],
                                              item_dict["media"])  # Create GetItem object
        self.last_updated = datetime.datetime.now().isoformat()  # Set the last updated time to now
        return result


class BaseItem:
    def __init__(self, name, id, price):
        """
        Instantiate a BaseItem object. This Item contains the very basic information of items.

        :param name: Item name
        :param id: Item id
        :param price: Item price
        """
        self.name = name
        self.id = id
        self.price = price


class GetItem(BaseItem):
    def __init__(self, name, id, price, folder, folder_id, published, media=""):
        """
        Instantiate a GetItem object. This Item contains all relevant information provided by the API response.

        :param name: Item name
        :param id: Item id
        :param price: Item price
        :param folder: Folder
        :param folder_id: Folder id
        :param published: True if the item is published, false otherwise
        :param media: (optional) Image URL
        """
        super().__init__(name, id, price)
        self.folder = folder
        self.folder_id = folder_id
        self.published = published
        self.media = media


class PostItem(BaseItem):
    def __init__(self, name, id, price, quantity):
        """
        Instantiate a PostItem object. This Item contains all relevant information to POST a sale to the API
        :param name: Item name
        :param id: Item id
        :param price: Item price
        :param quantity: Amount of this item to buy
        """
        super().__init__(name, id, price)
        self.quantity = quantity

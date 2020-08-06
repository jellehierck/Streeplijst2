import datetime

from streeplijst.config import FOLDERS
import streeplijst.api as api

def get_folder_from_config(folder_name):
    """
    Reads the config.py file and returns the Folder object with that name.

    :param folder_name: The folder name to read.
    :return: The Folder object
    """
    folder_dict = FOLDERS[folder_name]
    folder = Folder(folder_dict["name"], folder_dict["id"], folder_dict["media"])
    return folder


class Folder:
    def __init__(self, name, id, media=""):
        self.name = name  # Folder name
        self.id = id  # Folder id
        self.media = media  # Optional image URL
        self.last_updated = datetime.datetime.now().isoformat()
        self.items = self.get_items()  # Dict for all items

    def get_items(self):
        items_list = api.get_products_in_folder(self.id)
        result = dict()
        for item_dict in items_list:
            result[item_dict["id"]] = GetItem(item_dict["name"], item_dict["id"], item_dict["price"],
                                                  item_dict["folder"], item_dict["folder_id"], item_dict["published"],
                                                  item_dict["media"])
        return result


class BaseItem:
    def __init__(self, name, id, price):
        self.name = name
        self.id = id
        self.price = price


class GetItem(BaseItem):
    def __init__(self, name, id, price, folder, folder_id, published, media):
        super().__init__(name, id, price)
        self.folder = folder
        self.folder_id = folder_id
        self.published = published
        self.media = media


class PostItem(BaseItem):
    def __init__(self, name, id, price, quantity):
        super().__init__(name, id, price)
        self.quantity = quantity

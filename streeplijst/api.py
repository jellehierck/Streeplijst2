import requests
import json

from streeplijst.config import BASE_URL, base_header

def get_products_in_folder(folder_id):
    """
    GET all products inside a single folder from Congressus API.

    :param folder_id: Folder id to retrieve items for.
    :return: A list of dicts containing the server response converted from a JSON string.
    """
    url = BASE_URL + "products?folder_id=" + str(folder_id)
    res = requests.get(url=url, headers=base_header())
    res.json()
    return_list = json.loads(res.text)
    return return_list


def get_all_products():
    """
    GET all products in the folders specified in config.py.

    :return: all products.
    """
    pass


get_products_in_folder(1998)
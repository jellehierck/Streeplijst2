import requests
import json

from streeplijst.config import BASE_URL, FOLDERS, base_header

def get_products(folder_name="speciaal"):
    """
    GET all products inside a single folder from Congressus API.

    :param folder_name: Folder to retrieve products from
    :return:
    """
    folder = FOLDERS[folder_name]
    url = BASE_URL + "products?folder_id=" + str(folder["id"])
    r = requests.get(url=url, headers=base_header())
    r.json()
    obj = json.loads(r.text)
    for item in obj:
        print(item)


def get_all_products():
    """
    GET all products in the folders specified in config.py.

    :return: all products.
    """
    pass

if __name__ == "__main__":
    get_products()
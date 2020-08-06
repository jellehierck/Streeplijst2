import requests
import json

from streeplijst.config import BASE_URL, BASE_HEADER, TIMEOUT


def get_products_in_folder(folder_id):
    """
    GET all products inside a single folder from Congressus API. This is a blocking call.

    :param folder_id: Folder id to retrieve items for.
    :return: A list of dicts containing the server response converted from a JSON string.
    """
    url = BASE_URL + "products?folder_id=" + str(folder_id)  # Set the URL to connect to the API
    headers = BASE_HEADER  # Create the base header which contains the secret API token
    res = requests.get(url=url, headers=headers, timeout=TIMEOUT)  # Send the request with the default timeout
    res.json()  # Convert response to JSON
    result = json.loads(res.text)  # Select the relevant data and convert to a list of dicts
    return result


def get_user(s_number):
    """
    GET a single user from Congressus API. This is a blocking call.

    :param s_number: Student number to retrieve the user for.
    :return: A dict with containing the server response converted from a JSON string.
    """
    url = BASE_URL + "members?username=" + s_number  # Set the URL to connect to the API
    headers = BASE_HEADER  # Create the base header which contains the secret API token
    res = requests.get(url=url, headers=headers, timeout=TIMEOUT)  # Send the request with the default timeout
    res.json()  # Convert response to JSON
    result = json.loads(res.text)  # Convert response to a list of dicts. # Congressus always sends a list of objects.
    return result[0]  # We return the first dict in the list since there is only one object in the list.

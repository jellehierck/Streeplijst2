import requests  # library used for making calls to Congressus API
from requests import Timeout, HTTPError
import json
from datetime import datetime

from streeplijst2.config import BASE_URL, BASE_HEADER, TIMEOUT


class NotFoundException(requests.exceptions.HTTPError):
    """Error when something is not found."""


class ItemNotFoundException(NotFoundException):
    """Error when the item is not found."""


class FolderNotFoundException(NotFoundException):
    """Error when the folder is not found."""


class UserNotFoundException(NotFoundException):
    """Error when the user is not found."""


class UserNotSignedException(requests.exceptions.HTTPError):
    """Error when the user has no signed SDD mandate."""


def _normalize_media(item_dict):
    """
    Flatten the JSON dict for the media url, if the item has any.
    :param item_dict: JSON dict to flatten.
    """
    try:
        media = item_dict['media'][0]['url']
        item_dict['media'] = media
    except IndexError:
        item_dict['media'] = ''


def _normalize_profile_picture(user_dict):
    """
    Flatten the JSON dict for the profile picture, if the user has any.
    :param user_dict: JSON dict to flatten.
    """
    if user_dict['profile_picture'] is not None:  # TODO: Make this a try-except block like _normalize_media
        profile_picture = user_dict['profile_picture']['url']
        user_dict['profile_picture'] = profile_picture
    else:
        user_dict['profile_picture'] = ''


def get_product(item_id: int, timeout: float = TIMEOUT):
    """
    GET a single item from Congressus API.

    :param item_id: Item id to retrieve.
    :param timeout: Timeout for the request. Defaults to config.py TIMEOUT.
    :return: A dict containing the server response converted from a JSON string.
    """
    url = BASE_URL + '/products/' + str(item_id)
    headers = BASE_HEADER
    res = requests.get(url=url, headers=headers, timeout=timeout)

    if res.status_code == 404:
        error_msg = u'%s Client Error: Item %s is not found for URL %s' % (res.status_code, item_id, res.url)
        raise ItemNotFoundException(error_msg, response=res)  # Raise an HTTP error

    res.raise_for_status()  # Raise any other response errors
    result = json.loads(res.text)  # Select the relevant data and convert to a list of dicts
    _normalize_media(result)
    result['folder_name'] = result.pop('folder', None)  # Rename the folder field to folder_name
    result['price'] = int(result['price'])  # Convert the price from str to int
    return result


def get_products_in_folder(folder_id: int, timeout: float = TIMEOUT) -> list:
    """
    GET all products inside a single folder from Congressus API. This is a blocking call.

    :param folder_id: Folder id to retrieve items for.
    :param timeout: Timeout for the request. Defaults to config.py TIMEOUT.
    :return: A list of dicts containing the server response converted from a JSON string.
    """
    url = BASE_URL + "/products?folder_id=" + str(folder_id)  # Set the URL to connect to the API
    headers = BASE_HEADER  # Create the base header which contains the secret API token
    res = requests.get(url=url, headers=headers, timeout=timeout)  # Send the request with the default timeout

    res.raise_for_status()  # Raise any HTTP errors which occurred when making the request
    if not res.json():  # The server sent an empty response
        res.status_code = 404
        error_msg = u'%s Client Error: folder_id %s is not found for URL %s' % (res.status_code, folder_id, res.url)
        raise FolderNotFoundException(error_msg, response=res)  # Raise an HTTP error

    result = json.loads(res.text)  # Select the relevant data and convert to a list of dicts
    for item in result:
        _normalize_media(item)
        # Normalise the field results
        item['folder_name'] = item.pop('folder', None)  # Rename the folder field to folder_name
        item['price'] = int(item['price'])  # Convert the price from str to int

    return result


def get_user(s_number: str, timeout: float = TIMEOUT):
    """
    GET a single user from Congressus API. This is a blocking call.

    :param s_number: Student number to retrieve the user for.
    :param timeout: Timeout for the request. Defaults to config.py TIMEOUT.
    :return: A dict containing the server response converted from a JSON string.
    """
    url = BASE_URL + "/members?username=" + s_number  # Set the URL to connect to the API
    headers = BASE_HEADER  # Create the base header which contains the secret API token
    res = requests.get(url=url, headers=headers, timeout=timeout)  # Send the request with the default timeout

    res.raise_for_status()  # Raise any HTTP errors which occurred when making the request
    if not res.json():  # The server sent an empty response
        res.status_code = 404
        error_msg = u'%s Client Error: User %s is not found for URL %s' % (res.status_code, s_number, res.url)
        raise UserNotFoundException(error_msg, response=res)  # Raise an HTTP error

    user_list = json.loads(res.text)  # Convert response to a list of dicts. Congressus always sends a list of objects
    result = user_list[0]  # There will only be one user in this list, so we select the first user

    # Normalize the result fields
    result['date_of_birth'] = datetime.fromisoformat(result['date_of_birth'])
    result['s_number'] = result.pop('username', None)  # Rename the username field to s_number
    result['last_name'] = result.pop('primary_last_name_main', None)  # Rename to last_name
    result['last_name_prefix'] = result.pop('primary_last_name_prefix', None)  # Rename to last_name_prefix
    _normalize_profile_picture(result)

    return result


def post_sale(user_id: int, product_id: int, quantity: int, timeout: float = TIMEOUT):
    """
    POSTs a sale to Congressus API. This method may raise exceptions if the request is not valid or legal. Warning: This
    will add payments to a user.

    :param user_id: User ID to post to.
    :param product_id: Product ID.
    :param quantity: Amount to buy.
    :param timeout: Timeout for the request. Defaults to config.py TIMEOUT.
    :return: A dict containing the server response converted from a JSON string.
    """
    payload = {  # Store the sales parameters in the format required by Congressus
        "user_id": user_id,  # User id
        "items": [{"product_id": product_id,  # Product id
                   "quantity": quantity  # Amount of items
                   }], "payments": [{"type": "direct_debit"  # Type of payment
                                     # TODO: Direct debit is hard coded right now. This may be changed later, although
                                     #  the streeplijst is intended to only work with direct debit for now. See
                                     #  http://docs.congressus.nl/#!/default/post_sales for more info.
                                     }]}
    url = BASE_URL + "/sales"
    headers = BASE_HEADER
    res = requests.post(url=url, headers=headers, json=payload,
                        timeout=timeout)  # Send request with payload and default timeout

    # A user might not have signed their SDD mandate (SEPA machtiging) in which case POSTing a sale is forbidden.
    # Congressus returns a 404 (NOT FOUND) error but that should be a 403 (FORBIDDEN) error. That is corrected below.
    if res.status_code == 404 and "mandate" in res.text:  # If the server returned a mandate error
        res.status_code = 403  # This error should be a 403 error, which is why the code is changed here
        res.reason = 'FORBIDDEN'
        res.text.replace('404', '403')  # Replace the wrong error code in the response text
        error_msg = u'%s Client Error: User has no signed SDD mandate' % (res.status_code)
        raise UserNotSignedException(error_msg, response=res)  # Raise the mandate exception

    res.raise_for_status()  # Raise any other HTTP errors which occurred when making the request
    result = json.loads(res.text)  # Convert the entire response text to a python object

    for item in result['items']:  # Normalise the field results
        item['price'] = int(item['price'])  # Convert the price from str to int
        item['total_price'] = int(item['total_price'])  # Convert the total_price from str to int

    result['created'] = datetime.fromisoformat(result['created'])
    # result['modified'] = datetime.fromisoformat(result['modified'])  # TODO: This string might be empty, handle that

    return result

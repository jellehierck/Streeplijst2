import requests  # library used for making calls to Congressus API
import json

from streeplijst2.config import BASE_URL, BASE_HEADER, TIMEOUT


class FolderNotFoundException(requests.exceptions.HTTPError):
    """Error when the folder is not found."""


class UserNotFoundException(requests.exceptions.HTTPError):
    """Error when the user is not found."""


class UserNotSignedException(requests.exceptions.HTTPError):
    """Error when the user has no signed SDD mandate."""


def get_products_in_folder(folder_id, timeout=TIMEOUT):
    """
    GET all products inside a single folder from Congressus API. This is a blocking call.

    :param folder_id: Folder id to retrieve items for.
    :return: A list of dicts containing the server response converted from a JSON string.
    """
    url = BASE_URL + "/products?folder_id=" + str(folder_id)  # Set the URL to connect to the API
    headers = BASE_HEADER  # Create the base header which contains the secret API token
    res = requests.get(url=url, headers=headers, timeout=timeout)  # Send the request with the default timeout

    res.raise_for_status()  # Raise any HTTP errors which occurred when making the request
    if not res.json():  # The server sent an empty response
        res.status_code = 404
        error_msg = u'%s Server Error: folder_id %s is not found for URL %s' % \
                    (res.status_code, folder_id, res.url)
        raise FolderNotFoundException(error_msg, response=res)  # Raise an HTTP error

    result = json.loads(res.text)  # Select the relevant data and convert to a list of dicts
    return result


def get_user(s_number, timeout=TIMEOUT):
    """
    GET a single user from Congressus API. This is a blocking call.

    :param s_number: Student number to retrieve the user for.
    :param timeout: Timeout to
    :return: A dict with containing the server response converted from a JSON string.
    """
    url = BASE_URL + "/members?username=" + s_number  # Set the URL to connect to the API
    headers = BASE_HEADER  # Create the base header which contains the secret API token
    res = requests.get(url=url, headers=headers, timeout=timeout)  # Send the request with the default timeout

    res.raise_for_status()  # Raise any HTTP errors which occurred when making the request
    if not res.json():  # The server sent an empty response
        res.status_code = 404
        error_msg = u'%s Server Error: User %s is not found for URL %s' % \
                    (res.status_code, s_number, res.url)
        raise UserNotFoundException(error_msg, response=res)  # Raise an HTTP error

    result = json.loads(res.text)  # Convert response to a list of dicts. # Congressus always sends a list of objects.
    return result[0]  # We return the first dict in the list since there should be only one object in the list.


def post_sale(user_id, product_id, quantity, timeout=TIMEOUT):
    payload = {  # Store the sales parameters in the format required by Congressus
            "user_id": user_id,  # User id
            "items": [{
                    "product_id": product_id,  # Product id
                    "quantity": quantity  # Amount of items
            }],
            "payments": [{
                    "type": "direct_debit"  # Type of payment
                    # TODO: Direct debit is hard coded right now. This may be changed later, although the streeplijst
                    #  is intended to only work with direct debit for now. See
                    #  http://docs.congressus.nl/#!/default/post_sales for more info.
            }]
    }
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
        error_msg = u'%s Server Error: User has no signed SDD mandate' % (res.status_code)
        raise UserNotSignedException(error_msg, response=res)  # Raise the mandate exception

    res.raise_for_status()  # Raise any other HTTP errors which occurred when making the request
    result = json.loads(res.text)  # Convert the entire response text to a python object
    return result

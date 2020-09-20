import pytest
from requests.exceptions import HTTPError, Timeout

import streeplijst2.api as api
from streeplijst2.config import FOLDERS, TEST_FOLDER_ID, TEST_USER, TEST_USER_NO_SDD, TEST_ITEM

""""
Unit tests for API module.

These tests assume the following to be true in Congressus:

- The correct_user, correct_item, correct_folder and no_sdd_user exist in Congressus.
- The correct_user has signed their SDD mandate (required to post sales).
- The no_sdd_user has not signed their SDD mandate.
- The correct_item is a test item which costs EUR 0,00.
- The correct_item is stored in the correct_folder.

- The incorrect_user, incorrect_item and incorrect_folder all do not exist in Congressus.

You can change the values in the global variables below.
"""

correct_user = TEST_USER
correct_item = TEST_ITEM
correct_folder = FOLDERS[TEST_FOLDER_ID]

no_sdd_user = TEST_USER_NO_SDD

incorrect_user = dict({"s_number": "s8888888", "id": 0})
incorrect_item = dict({"id": 1})
incorrect_folder = dict({"id": 1})


# Test if a valid folder id returns a response with the correct items
def test_get_products_in_folder_correct():
    res = api.get_products_in_folder(correct_folder["id"])

    # Check if there are responses with the correct key in the response
    assert any("id" in item for item in res)
    # Check if there is an item in the response which corresponds to the test item
    assert any(correct_item["id"] == item["id"] for item in res)


# Test if an invalid folder id raises the correct exception
def test_get_products_in_folder_incorrect():
    with pytest.raises(HTTPError) as error:
        res = api.get_products_in_folder(incorrect_folder["id"])
    assert "404 Client Error: folder_id " + str(incorrect_folder["id"]) + " is not found" in str(error.value)

    # Test if the timeout exception is raised
    with pytest.raises(Timeout) as error:
        api.get_products_in_folder(correct_folder["id"], 0.001)


# Test if a valid username returns a response with correct data
def test_get_user_correct():
    res = api.get_user(correct_user["s_number"])
    assert "first_name" in res and correct_user["first_name"] == res["first_name"]

    res = api.get_user(no_sdd_user["s_number"])
    assert "first_name" in res and no_sdd_user["first_name"] == res["first_name"]


# Test if an invalid username raises the correct exception
def test_get_user_incorrect():
    with pytest.raises(api.UserNotFoundException) as error:
        res = api.get_user(incorrect_user["s_number"])
    assert "404 Client Error: User " + incorrect_user["s_number"] + " is not found" in str(error.value)

    # Test if the timeout exception is raised
    with pytest.raises(Timeout) as error:
        api.get_user(correct_user["s_number"], 0.001)


# Test if a valid item_id returns a response with correct data
def test_get_item_correct():
    res = api.get_product(correct_item["id"])
    assert "name" in res and correct_item["name"] == res["name"]
    assert 'folder_id' in res and correct_item['folder_id'] == res['folder_id']


def test_get_item_incorrect():
    with pytest.raises(api.ItemNotFoundException) as error:
        res = api.get_product(incorrect_item["id"])
    assert "404 Client Error: Item " + str(incorrect_item["id"]) + " is not found" in str(error.value)

    # Test if the timeout exception is raised
    with pytest.raises(Timeout) as error:
        api.get_product(correct_item["id"], 0.001)


# Test if a correct sale can be posted
def test_post_sale_correct():
    res = api.post_sale(correct_user["id"], correct_item["id"], 1)


# Test if various incorrect sales raise the correct exceptions
def test_post_sale_incorrect():
    # Incorrect user
    with pytest.raises(HTTPError) as error:
        res = api.post_sale(incorrect_user["id"], correct_item["id"], 1)
    assert "404" in str(error.value)

    # Incorrect item
    with pytest.raises(HTTPError) as error:
        res = api.post_sale(correct_user["id"], incorrect_item["id"], 1)
    assert "404" in str(error.value)

    # Timeout
    with pytest.raises(Timeout) as error:
        res = api.post_sale(correct_user["id"], correct_item["id"], 1, 0.001)

    # No SDD sign on user
    with pytest.raises(api.UserNotSignedException) as error:
        res = api.post_sale(no_sdd_user["id"], correct_item["id"], 1)
    assert str(403) in str(error.value) and "mandate" in str(error.value)


def test_normalize_media():
    item_dict_with_media = {'media': [
        {'url': 'www.url.com'}
    ]}
    api._normalize_media(item_dict_with_media)
    assert item_dict_with_media['media'] == 'www.url.com'

    item_dict_without_media = {'media': []}
    api._normalize_media(item_dict_without_media)
    assert item_dict_without_media['media'] == ''


def test_normalize_profile_picture():
    user_with_profile_pic = {'profile_picture':
                                 {'url': 'www.url.com'}
                             }
    api._normalize_profile_picture(user_with_profile_pic)
    assert user_with_profile_pic['profile_picture'] == 'www.url.com'

    user_without_profile_pic = {'profile_picture': None}
    api._normalize_profile_picture(user_without_profile_pic)
    assert user_without_profile_pic['profile_picture'] == ''

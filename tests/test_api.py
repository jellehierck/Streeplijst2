import pytest
from requests.exceptions import HTTPError, Timeout

import streeplijst2.api as api

""""
Unit tests for API module.

These tests assume the following to be true in Congressus:

- The correct_user, correct_item and correct_folder exist in Congressus.
- The correct_user has signed their SDD mandate (required to post sales).
- The correct_item is a test item which costs EUR 0,00.
- The correct_item is stored in the correct_folder.

- The incorrect_user, incorrect_item and incorrect_folder all do not exist in Congressus.

You can change the values in the global variables below.
"""

correct_user = dict({'username': 's9999999', 'first_name': 'Test', 'user_id': 347980})
correct_item = dict({'id': 13591})
correct_folder = dict({'folder_id': 1998})

incorrect_user = dict({'username': 's8888888', 'user_id': 0})
incorrect_item = dict({'id': 1})
incorrect_folder = dict({'folder_id': 1})


# Test if a valid folder id returns a response with the correct items
def test_get_products_in_folder_correct():
    res = api.get_products_in_folder(correct_folder['folder_id'])

    # Check if there are responses with the correct key in the response
    assert any('id' in item for item in res)
    # Check if there is an item in the response which corresponds to the test item
    assert any(correct_item['id'] == item['id'] for item in res)


# Test if an invalid folder id raises the correct exception
def test_get_products_in_folder_incorrect():
    with pytest.raises(HTTPError) as error:
        res = api.get_products_in_folder(incorrect_folder['folder_id'])
    assert "200 Server Error: Request OK, but folder_id " + str(incorrect_folder['folder_id']) + \
           " is not found" in str(error.value)

    # Test if the timeout exception is raised
    with pytest.raises(Timeout) as error:
        api.get_products_in_folder(correct_folder['folder_id'], 0.001)


# Test if a valid username returns a response with correct data
def test_get_user_correct():
    res = api.get_user(correct_user['username'])
    assert 'first_name' in res and correct_user['first_name'] == res['first_name']


# Test if an invalid username raises the correct exception
def test_get_user_incorrect():
    with pytest.raises(HTTPError) as error:
        res = api.get_user(incorrect_user['username'])
    assert "200 Server Error: Request OK, but user " + incorrect_user['username'] + " is not found" in str(error.value)

    # Test if the timeout exception is raised
    with pytest.raises(Timeout) as error:
        api.get_user(correct_user['username'], 0.001)


# Test if a correct sale can be posted
def test_post_sale_correct():
    res = api.post_sale(correct_user['user_id'], correct_item['id'], 1)


# Test if various incorrect sales raise the correct exceptions
def test_post_sale_incorrect():
    # Incorrect user
    with pytest.raises(HTTPError) as error:
        res = api.post_sale(incorrect_user['user_id'], correct_item['id'], 1)
    assert "404" in str(error.value)

    # Incorrect item
    with pytest.raises(HTTPError) as error:
        res = api.post_sale(correct_user['user_id'], incorrect_item['id'], 1)
    assert "404" in str(error.value)

    # Timeout
    with pytest.raises(Timeout) as error:
        res = api.post_sale(correct_user['user_id'], correct_item['id'], 1, 0.001)

import pytest
from requests.exceptions import HTTPError, Timeout

import streeplijst2.api as api

correct_user = dict({'username': 's9999999', 'first_name': 'Test', 'user_id': 347980})
incorrect_user = dict({'username': 's8888888', 'user_id': 0})
correct_item = dict({'product_id': 13591})
incorrect_item = dict({'product_id': 1})


# Test if a valid username returns a response with correct data
def test_get_correct_user():
    res = api.get_user(correct_user['username'])
    assert 'first_name' in res and correct_user['first_name'] == res['first_name']


# Test if an invalid username raises the correct exception
def test_get_incorrect_user():
    with pytest.raises(HTTPError) as error:
        res = api.get_user(incorrect_user['username'])

    assert "200 Client Error: Request OK, but user " + incorrect_user["username"] + " is not found" in str(error.value)


# Test if the timeout exception is raised
def test_get_user_timeout():
    with pytest.raises(Timeout) as error:
        api.get_user(correct_user['username'], 0.001)


# Test if a correct sale can be posted
def test_post_correct_sale():
    res = api.post_sale(correct_user['user_id'], correct_item['product_id'], 1)


# Test if various incorrect sales raise the correct exceptions
def test_post_incorrect_sale():
    # Incorrect user
    with pytest.raises(HTTPError) as error:
        res = api.post_sale(incorrect_user['user_id'], correct_item['product_id'], 1)
    assert "404" in str(error.value)

    # Incorrect item
    with pytest.raises(HTTPError) as error:
        res = api.post_sale(correct_user['user_id'], incorrect_item['product_id'], 1)
    assert "404" in str(error.value)

    # Timeout
    with pytest.raises(Timeout) as error:
        res = api.post_sale(correct_user['user_id'], correct_item['product_id'], 1, 0.001)

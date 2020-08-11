import pytest
from requests.exceptions import HTTPError, Timeout

import streeplijst2.api as api

correct_user = dict({"username": "s9999999", "first_name": "Test"})
wrong_user = dict({"username": "s8888888"})


# Test if a valid username returns a response with correct data
def test_get_correct_user():
    res = api.get_user(correct_user["username"])
    assert "first_name" in res and correct_user["first_name"] == res["first_name"]


# Test if an invalid username raises the correct exception
def test_get_wrong_user():
    with pytest.raises(HTTPError) as error:
        res = api.get_user(wrong_user["username"])

    assert "200 Client Error: Request OK, but user s8888888 is not found" in str(error.value)


def test_get_user_timeout():
    with pytest.raises(Timeout) as error:
        api.get_user(correct_user["username"], 0.001)

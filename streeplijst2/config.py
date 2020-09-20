"""
Config.py

Contains all non-secure information for the flask_app.py file. This includes certain configurations for the Congressus API.
"""

from credentials import TOKEN  # Import the secure credentials from credentials.py

# CONSTANTS

TIMEOUT = 10
"""Default timeout time for server responses."""

BASE_URL = "https://api.congressus.nl/v20"
""""Base url for Congressus API calls."""

FOLDERS = {
    1991: {
        "name": "Chips",  # folder name
        "id": 1991,  # folder id (determined by Congressus, found in URL of the folder in the manager)
        "media": "https://www.paradoks.utwente.nl/_media/889901/afa76d9d15c44705a9b7ef4da818ef2c/view"
        # url to image file (found in Congressus)
    },
    1992: {
        "name": "Soep",
        "id": 1992,
        "media": "https://www.paradoks.utwente.nl/_media/889902/d1de3e30149f48238d7df0566454a55f/view"
    },
    1993: {
        "name": "Healthy",
        "id": 1993,
        "media": "https://www.paradoks.utwente.nl/_media/889906/447f0d874bcb48479b43dede97149183/view"
    },
    1994: {
        "name": "Diepvries",
        "id": 1994,
        "media": "https://www.paradoks.utwente.nl/_media/889938/a1be36b57e9d4cd4aba77a0a169ad8ed/view"
    },
    1995: {
        "name": "Snoep",
        "id": 1995,
        "media": "https://www.paradoks.utwente.nl/_media/889918/eda7aefce97745488c867c1fd46e580b/view"
    },
    1996: {
        "name": "Koek",
        "id": 1996,
        "media": "https://www.paradoks.utwente.nl/_media/889908/5bbaa93d68fb4886974309dd09e3920f/view"
    },
    1997: {
        "name": "Repen",
        "id": 1997,
        "media": "https://www.paradoks.utwente.nl/_media/889915/596ad94dc4fc42b6910d9648fed06aad/view"
    },
    1998: {
        "name": "Speciaal",
        "id": 1998,
        "media": "https://www.paradoks.utwente.nl/_media/889910/63b78b80f2224dff8c46bfb8456d0bc8/view"
    },
    2600: {
        "name": "Frisdrank",
        "id": 2600,
        "media": "https://www.paradoks.utwente.nl/_media/1074042/9737731eab49463eb625490e9d2d1b20/view"
    },
}
"""Folders which contain streeplijst items in Congressus. This format is used to make JSON calls directly to the API."""

BASE_HEADER = {
    "Authorization": "Bearer:" + TOKEN
}
"""Base authorization header using the secret API token."""

TEST_USER = {
    "s_number": "s9999999",
    "first_name": "Test",
    "id": 347980
}
"""Test user specification. Note: not all attributes are listed as they are not all needed."""

TEST_USER_NO_SDD = {
    "s_number": "s9999998",
    "first_name": "TestTwee",
    "id": 485567
}
"""Test user with no SDD mandate specification. Note: not all attributes are listed as they are not all needed."""

TEST_FOLDER_ID = 1998
"""Test folder id. This folder contains the test item."""

TEST_ITEM = {
    "id": 13591,
    "folder_id": TEST_FOLDER_ID,
    "name": "Testproduct"
}
"""Test item specification. Note: not all attributes are listed as they are not all needed."""

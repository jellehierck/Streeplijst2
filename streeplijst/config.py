"""
Config.py

Contains all non-secure information for the app.py file. This includes certain configurations for the Congressus API.
"""

from credentials import TOKEN  # Import the secure credentials from credentials.py

# CONSTANTS

TIMEOUT = 10
"""Default timeout time for server responses."""

BASE_URL = "https://api.congressus.nl/v20/"
""""Base url for Congressus API calls."""

FOLDERS = {
        "Chips": {
                "name": "Chips",  # folder name
                "id": 1991,  # folder id (determined by Congressus, found in URL of the folder in the manager)
                "media": "https://www.paradoks.utwente.nl/_media/889901/afa76d9d15c44705a9b7ef4da818ef2c/view"
                # url to image file (found in Congressus)
        },
        "Soep": {
                "name": "Soep",
                "id": 1992,
                "media": "https://www.paradoks.utwente.nl/_media/889902/d1de3e30149f48238d7df0566454a55f/view"
        },
        "Healthy": {
                "name": "Healthy",
                "id": 1993,
                "media": "https://www.paradoks.utwente.nl/_media/889906/447f0d874bcb48479b43dede97149183/view"
        },
        "Diepvries": {
                "name": "Diepvries",
                "id": 1994,
                "media": "https://www.paradoks.utwente.nl/_media/889938/a1be36b57e9d4cd4aba77a0a169ad8ed/view"
        },
        "Snoep": {
                "name": "Snoep",
                "id": 1995,
                "media": "https://www.paradoks.utwente.nl/_media/889918/eda7aefce97745488c867c1fd46e580b/view"
        },
        "Koek": {
                "name": "Koek",
                "id": 1996,
                "media": "https://www.paradoks.utwente.nl/_media/889908/5bbaa93d68fb4886974309dd09e3920f/view"
        },
        "Repen": {
                "name": "Repen",
                "id": 1997,
                "media": "https://www.paradoks.utwente.nl/_media/889915/596ad94dc4fc42b6910d9648fed06aad/view"
        },
        "Speciaal": {
                "name": "Speciaal",
                "id": 1998,
                "media": "https://www.paradoks.utwente.nl/_media/889910/63b78b80f2224dff8c46bfb8456d0bc8/view"
        },
        "Frisdrank": {
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

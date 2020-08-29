import pytest
from requests.exceptions import HTTPError, Timeout

from streeplijst2.config import FOLDERS, TEST_ITEM, TEST_USER, TEST_USER_NO_SDD, TEST_FOLDER_NAME
from streeplijst2.streeplijst import Folder, User, Sale
from streeplijst2.api import UserNotSignedException

test_folder = FOLDERS[TEST_FOLDER_NAME]


def test_folder_init():
    """
    Test that the folder correctly initializes.
    """
    folder = Folder(name=test_folder['name'], id=test_folder['id'], media=test_folder['media'])
    assert folder.items is None  # Test if there are no items in the folder upon initialization
    assert folder.last_updated is None  # Test if the folder is not yet updated


def test_folder_update_items():
    """
    Test that the folder updates correctly.
    """
    folder = Folder(name=test_folder['name'], id=test_folder['id'], media=test_folder['media'])
    folder.update_items()
    assert folder.items is not None  # Test if there are items in the folder
    assert any(TEST_ITEM['id'] == item.id for item in folder.items.values())  # Test if the test item exists in folder
    assert folder.last_updated is not None  # Test if the updated string is set


def test_folder_from_config():
    """
    Test that the folder can be initialized from config.py and produces the correct results.
    """
    folder = Folder.from_config(folder_name=TEST_FOLDER_NAME)
    assert folder.items is not None  # Test if there are items in the folder
    assert any(TEST_ITEM['id'] == item.id for item in folder.items.values())  # Test if the test item exists in folder
    assert folder.last_updated is not None  # Test if the updated string is set


def test_folder_all_folders_from_config():
    """
    Test that all folders in config.py can be loaded and produce the correct results.
    """
    all_folders = Folder.all_folders_from_config()
    assert all_folders is not None  # Test if there are folders in the resulting dict
    assert any(test_folder['id'] == folder.id for folder in all_folders.values())  # Test if the test folder exists


def test_user_from_api():
    user = User.from_api(TEST_USER['s_number'])
    assert TEST_USER['id'] == user.id
    assert TEST_USER['first_name'] == user.first_name
    assert TEST_USER['s_number'] == user.s_number


def test_sale_post_sale():
    folder = Folder.from_config(TEST_FOLDER_NAME)  # Load the test folder (needed for test item)
    item = folder.items[TEST_ITEM['id']]  # Load the test item
    user = User.from_api(TEST_USER['s_number'])  # Load the test user

    sale = Sale(user, item, 1)  # Create a single sale of the test item
    response = sale.post_sale()

    assert response is not None


def test_sale_post_sale_errors():
    folder = Folder.from_config(TEST_FOLDER_NAME)  # Load the test folder (needed for test item)
    item = folder.items[TEST_ITEM['id']]  # Load the test item
    user = User.from_api(TEST_USER['s_number'])  # Load the test user
    no_sdd_user = User.from_api(TEST_USER_NO_SDD['s_number'])  # Load the user without SDD mandate

    # Incorrect user
    with pytest.raises(HTTPError) as error:
        user.id = 0  # Set the user ID to a false value
        sale = Sale(user, item, 1)
        res = sale.post_sale()
    assert "404" in str(error.value)
    user.id = TEST_USER['id']  # Set the user ID back to the correct value

    # Incorrect item
    with pytest.raises(HTTPError) as error:
        item.id = 1  # Set the item ID to a false value
        sale = Sale(user, item, 1)
        res = sale.post_sale()
    assert "404" in str(error.value)
    item.id = TEST_ITEM['id']  # Set the item ID back to the correct value

    # No SDD sign on user
    with pytest.raises(UserNotSignedException) as error:
        sale = Sale(no_sdd_user, item, 1)
        res = sale.post_sale()
    assert str(403) in str(error.value) and "mandate" in str(error.value)

    # Timeout
    with pytest.raises(Timeout) as error:
        sale = Sale(user, item, 1)
        res = sale.post_sale(timeout=0.001)

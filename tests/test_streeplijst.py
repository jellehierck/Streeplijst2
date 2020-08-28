import pytest

from streeplijst2.config import FOLDERS
from streeplijst2.streeplijst import Folder, User

test_folder_name = "Speciaal"
test_folder = FOLDERS[test_folder_name]
test_item = dict({'id': 13591, 'folder': test_folder_name, 'name': "Testproduct"})
test_user = dict({'s_number': 's9999999', 'first_name': 'Test', 'id': 347980})

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
    assert any(test_item['id'] == item.id for item in folder.items.values())  # Test if the test item exists in folder
    assert folder.last_updated is not None  # Test if the updated string is set


def test_folder_from_config():
    """
    Test that the folder can be initialized from config.py and produces the correct results.
    """
    folder = Folder.from_config(folder_name=test_folder_name)
    assert folder.items is not None  # Test if there are items in the folder
    assert any(test_item['id'] == item.id for item in folder.items.values())  # Test if the test item exists in folder
    assert folder.last_updated is not None  # Test if the updated string is set


def test_folder_all_folders_from_config():
    """
    Test that all folders in config.py can be loaded and produce the correct results.
    """
    all_folders = Folder.all_folders_from_config()
    assert all_folders is not None  # Test if there are folders in the resulting dict
    assert any(test_folder['id'] == folder.id for folder in all_folders.values())  # Test if the test folder exists


def test_user_from_api():
    user = User.from_api(test_user['s_number'])
    assert test_user['id'] == user.id
    assert test_user['first_name'] == user.first_name
    assert test_user['s_number'] == user.s_number

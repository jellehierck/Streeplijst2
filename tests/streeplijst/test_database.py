# from requests.exceptions import Timeout
#
# from streeplijst2.api import FolderNotFoundException, UserNotFoundException
# from streeplijst2.streeplijst.database import StreeplijstDBController as db_controller
from streeplijst2.config import TEST_FOLDER
from streeplijst2.streeplijst.database import FolderDB, ItemDB
import streeplijst2.api as api

TEST_FOLDER_NO_MEDIA = TEST_FOLDER
TEST_FOLDER_NO_MEDIA.pop('media', None)  # Remove the media field

TEST_FOLDER_UPDATED = dict({
    'name': 'New Folder Name',
    'media': 'www.media.url'
})

TEST_FOLDER_2 = dict({
    'id': 1,
    'name': 'test folder 2',
    'media': ''
})


class TestFolder:

    def test_create_folder(self, test_app):
        with test_app.app_context():
            folder = FolderDB.create(**TEST_FOLDER)
            for (key, value) in TEST_FOLDER.items():  # Make sure all fields are stored correctly
                assert folder.__getattribute__(key) == value

    def test_create_folder_no_media(self, test_app):
        with test_app.app_context():
            folder = FolderDB.create(**TEST_FOLDER_NO_MEDIA)
            for (key, value) in TEST_FOLDER_NO_MEDIA.items():  # Make sure all fields are stored correctly
                assert folder.__getattribute__(key) == value
            assert folder.__getattribute__('media') is None

    def test_get_folder(self, test_app):
        with test_app.app_context():
            folder = FolderDB.create(**TEST_FOLDER)
            other_folder = FolderDB.get(TEST_FOLDER['id'])
            assert folder is other_folder

    def test_update_folder(self, test_app):
        with test_app.app_context():
            folder = FolderDB.create(**TEST_FOLDER)
            updated_folder = FolderDB.update(TEST_FOLDER['id'], **TEST_FOLDER_UPDATED)
            for (key, value) in TEST_FOLDER_UPDATED.items():  # Make sure all values are updated as expected
                assert updated_folder.__getattribute__(key) == value
                assert folder.__getattribute__(key) == updated_folder.__getattribute__(key)

    def test_delete_folder(self, test_app):
        with test_app.app_context():
            folder = FolderDB.create(**TEST_FOLDER)
            get_folder = FolderDB.get(TEST_FOLDER['id'])
            assert get_folder is not None  # Make sure the user is retrieved

            deleted_folder = FolderDB.delete(TEST_FOLDER['id'])
            assert folder is deleted_folder  # Make sure the same object is referenced

            get_folder = FolderDB.get(TEST_FOLDER['id'])
            assert get_folder is None  # Make sure the user is not retrieved

    def test_list_all_folders(self, test_app):
        with test_app.app_context():
            folder1 = FolderDB.create(**TEST_FOLDER)
            folder2 = FolderDB.create(**TEST_FOLDER_2)
            folder_list = FolderDB.list_all()
            assert len(folder_list) == 2
            assert folder2 == folder_list[0]  # folder2 has lower id so be first in the list
            assert folder1 == folder_list[1]


class TestFolderAPI:

    def test_create_folder_and_items(self, test_app):
        with test_app.app_context():
            folder = FolderDB.create(**TEST_FOLDER)
            items = api.get_products_in_folder(folder.id)
            for item_dict in items:
                item = ItemDB.create(**item_dict)

# def test_create_folder_folder_id(test_app):
#     """
#     Test that the folder can be initialized from config.py and produces the correct results.
#     """
#     with test_app.app_context():
#         folder = db_controller.create_folder(folder_id=TEST_FOLDER_ID)
#         assert folder.items is not None  # Test if there are items in the folder
#         assert folder.get_item(TEST_ITEM['id']) is not None  # Test if test item exists in folder
#         assert folder.last_synchronized is not None  # Test if the updated string is set
#
#
# def test_create_folder_mapping(test_app):
#     """
#     Test that all folders in config.py can be loaded and produce the correct results.
#     """
#     with test_app.app_context():
#         folder = db_controller.create_folder(mapping=test_folder)
#         assert folder.items is not None  # Test if there are items in the folder
#         assert folder.get_item(TEST_ITEM['id']) is not None  # Test if test item exists in folder
#         assert folder.last_synchronized is not None  # Test if the updated string is set
#
#
# def test_create_folder_errors(test_app):
#     with test_app.app_context():
#         with pytest.raises(FolderNotFoundException) as err:
#             folder = db_controller.create_folder(mapping={'name': 'nonexistent', 'id': 1, 'media': ''})
#         assert '404 Client Error: folder_id 1 is not found for URL' in str(err.value)
#
#         with pytest.raises(TypeError) as err:
#             folder = db_controller.create_folder()
#
#
# def test_create_sale(test_app):
#     with test_app.app_context():
#         item = db_controller.create_item(item_id=TEST_ITEM['id'])
#         user = db_controller.create_user(s_number=TEST_USER['s_number'])
#         sale = db_controller.create_sale(item_id=item.id, user_id=user.id, quantity=1)
#
#
# def test_create_sale_errors(test_app):
#     with test_app.app_context():
#         item = db_controller.create_item(item_id=TEST_ITEM['id'])
#         incorrect_user_id = 1
#         assert not db_controller.create_sale(item_id=item.id, user_id=incorrect_user_id, quantity=1)
#
#
# def test_get_folder(test_app):
#     with test_app.app_context():
#         folder = db_controller.get_folder(folder_id=TEST_FOLDER_ID)
#         assert not folder  # Ensure the folder does not exist in the database
#
#         folder = db_controller.create_folder(folder_id=TEST_FOLDER_ID)
#         assert folder
#         assert db_controller.get_folder(folder_id=TEST_FOLDER_ID)
#
#
# def test_get_folder_sync(test_app):
#     with test_app.app_context():
#         folder = db_controller.create_folder(folder_id=TEST_FOLDER_ID)  # Create the folder
#         last_synchronized = folder.last_synchronized  # Store when the folder was synchronized
#
#         # Do not sync folder
#         folder = db_controller.get_folder(folder_id=TEST_FOLDER_ID, sync=False)
#         assert last_synchronized == folder.last_synchronized
#
#         # Sync folder but do not force sync (should not sync)
#         folder = db_controller.get_folder(folder_id=TEST_FOLDER_ID, sync=True, force_sync=False, update_interval=5)
#         assert last_synchronized == folder.last_synchronized
#
#         # Sync folder and force sync
#         folder = db_controller.get_folder(folder_id=TEST_FOLDER_ID, sync=True, force_sync=True)
#         assert last_synchronized != folder.last_synchronized
#
#
# def test_get_or_create_folder(test_app):
#     with test_app.app_context():
#         # Test that a folder is created
#         folder = db_controller.get_or_create_folder(folder_id=TEST_FOLDER_ID, auto_commit=True)
#         assert folder is not None
#
#         # Test that getting a folder returns a folder and does not create a new one
#         folder2 = db_controller.get_or_create_folder(folder_id=TEST_FOLDER_ID, auto_commit=True)
#         assert folder is folder2  # Ensure the folders returned are the same
#
#         # Test that syncing does not change the folder
#         folder3 = db_controller.get_or_create_folder(folder_id=TEST_FOLDER_ID, sync=True, force_sync=True,
#                                                      auto_commit=True)
#         assert folder is folder3  # Ensure the folders returned are the same
#
#
# def test_get_item(test_app):
#     with test_app.app_context():
#         item = db_controller.get_item(item_id=TEST_ITEM['id'])
#         assert not item  # Ensure the item does not exist in the database
#
#         item = db_controller.create_item(item_id=TEST_ITEM['id'])
#         assert item
#         assert db_controller.get_item(item_id=TEST_ITEM['id'])  # Ensure the item exists in the database
#
#
# def test_sync_folder(test_app):
#     with test_app.app_context():
#         folder = db_controller.create_folder(folder_id=TEST_FOLDER_ID)
#         last_synchronized = folder.last_synchronized  # Folder is synced upon creation
#
#         # This should not update the folder as it is less than 5 minutes ago it was created
#         db_controller.sync_folder(folder.id, force_sync=False, update_interval=5, auto_commit=True)
#         assert folder.last_synchronized == last_synchronized
#
#         # The folder is forcefully updated and should now update its .last_synchronized field
#         db_controller.sync_folder(folder.id, force_sync=True, update_interval=5, auto_commit=True)
#         assert folder.last_synchronized != last_synchronized
#
#         last_synchronized = folder.last_synchronized
#         db_controller.sync_folder(folder.id, force_sync=False, update_interval=0, auto_commit=True)
#         assert folder.last_synchronized != last_synchronized

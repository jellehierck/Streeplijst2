# from requests.exceptions import Timeout
#
# from streeplijst2.api import FolderNotFoundException, UserNotFoundException
# from streeplijst2.streeplijst.database import StreeplijstDBController as db_controller
import pytest
import copy
from datetime import datetime, timedelta
import time

from streeplijst2.config import TEST_FOLDER, TEST_USER, TEST_ITEM, TEST_USER_NO_SDD, TEST_ITEM_2
from streeplijst2.database import UserDB
from streeplijst2.streeplijst.database import FolderDB, ItemDB, NotInDatabaseException, SaleDB, Sale
import streeplijst2.api as api

TEST_FOLDER_NO_MEDIA = copy.deepcopy(TEST_FOLDER)
TEST_FOLDER_NO_MEDIA.pop('media', None)  # Remove the media field

TEST_FOLDER_UPDATED = dict({
    'id': TEST_FOLDER['id'],
    'name': 'New Folder Name',
    'media': 'www.media.url'
})

TEST_FOLDER_2 = dict({
    'id': 1,
    'name': 'test folder 2',
    'media': ''
})

TEST_SALE = dict({
    'quantity': 1,
    'total_price': 0,
    'item_id': TEST_ITEM['id'],
    'item_name': TEST_ITEM['name'],
    'user_id': TEST_USER['id'],
    'user_s_number': TEST_USER['s_number'],
})

TEST_SALE_2 = copy.deepcopy(TEST_SALE)
TEST_SALE_2.update(dict({
    'user_id': TEST_USER_NO_SDD['id'],
    'user_s_number': TEST_USER_NO_SDD['s_number'],
    'item_id': TEST_ITEM_2['id'],
    'item_name': TEST_ITEM_2['name'],
}))


class TestFolder:

    def test_create_folder(self, test_app):
        with test_app.app_context():
            folder = FolderDB.create(**TEST_FOLDER)
            for (key, value) in TEST_FOLDER.items():  # Make sure all fields are stored correctly
                assert folder.__getattribute__(key) == value
            assert folder.synchronized == datetime.min

    def test_create_folder_existing(self, test_app):
        with test_app.app_context():
            folder = FolderDB.create(**TEST_FOLDER)
            updated_folder = FolderDB.create(**TEST_FOLDER_UPDATED)
            for (key, value) in TEST_FOLDER_UPDATED.items():  # Make sure all values are updated as expected
                assert updated_folder.__getattribute__(key) == value
                assert folder.__getattribute__(key) == updated_folder.__getattribute__(key)

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
            updated_folder = FolderDB.update(**TEST_FOLDER_UPDATED)
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

    def test_get_items_in_folder(self, test_app):
        with test_app.app_context():
            folder = FolderDB.create(**TEST_FOLDER)
            items = FolderDB.get_items_in_folder(folder.id)
            assert len(items) == 0  # Make sure there are no items in


class TestFolderAPI:

    def test_load_folder(self, test_app):
        with test_app.app_context():
            initial_folder = FolderDB.create(**TEST_FOLDER)
            folder = FolderDB.load_folder(TEST_FOLDER['id'])  # folder should synchronize because it was just created
            last_synchronized = folder.synchronized
            assert initial_folder is folder  # Test that they reference the same object
            assert last_synchronized > \
                   datetime.now() - timedelta(seconds=1)  # Test if synchronized time is set to (almost) now
            assert len(FolderDB.get_items_in_folder(folder.id)) != 0  # Test if there are items in the folder now

            folder2 = FolderDB.load_folder(folder.id, force_sync=False,
                                           auto_sync_interval=10)  # Load the folder from the database (no sync)
            assert folder is folder2

            folder3 = FolderDB.load_folder(folder.id, force_sync=True)  # Force load the folder from API
            assert folder is folder3

    def test_load_folder_update_interval(self, test_app):
        with test_app.app_context():
            FolderDB.create(**TEST_FOLDER)
            folder = FolderDB.load_folder(TEST_FOLDER['id'])
            last_synchronized = folder.synchronized  # Store when the folder was synchronized

            folder = FolderDB.load_folder(TEST_FOLDER['id'], force_sync=False,
                                          auto_sync_interval=10)  # Load folder from db without sync
            assert folder.synchronized == last_synchronized  # Test that the folder was not synchronized

            time.sleep(1)  # Sleep to allow the auto_sync_interval
            folder = FolderDB.load_folder(TEST_FOLDER['id'], force_sync=False, auto_sync_interval=0.5)  # sync folder
            assert folder.synchronized > last_synchronized  # Test that the folder was synchronized

    def test_load_folder_not_in_db(self, test_app):
        with test_app.app_context():
            with pytest.raises(NotInDatabaseException):
                folder = FolderDB.load_folder(TEST_FOLDER['id'])


class TestItem:

    def test_list_all_items(self, test_app):
        with test_app.app_context():
            item1 = ItemDB.create(**TEST_ITEM)
            item2 = ItemDB.create(**TEST_ITEM_2)
            item_list = ItemDB.list_all()
            assert len(item_list) == 2
            if item1.id < item2.id:  # Order of return is based on id, so make sure to test the right return order
                assert item_list[0] is item1 and item_list[1] == item2
            else:
                assert item_list[0] is item2 and item_list[1] == item1

    def test_delete_item(self, test_app):
        with test_app.app_context():
            item = ItemDB.create(**TEST_ITEM)
            assert len(ItemDB.list_all()) == 1

            deleted_item = ItemDB.delete(TEST_ITEM['id'])
            assert deleted_item is item
            assert len(ItemDB.list_all()) == 0


class TestSale:

    def test_create_sale(self, test_app):
        with test_app.app_context():
            sale = SaleDB.create(**TEST_SALE)
            for (key, value) in TEST_SALE.items():  # Make sure all fields are stored correctly
                assert sale.__getattribute__(key) == value
            assert sale.id == 1  # The ID autoincrements, starting at 1
            assert sale.status == Sale.STATUS_NOT_POSTED  # Test the status
            assert sale.api_id is None and sale.api_created is None and sale.error_msg is None  # Test None fields

    def test_create_quick_sale(self, test_app):
        with test_app.app_context():
            item = ItemDB.create(**TEST_ITEM)
            user = UserDB.create(**TEST_USER)
            sale = SaleDB.create_quick(quantity=1, item_id=item.id, user_id=user.id)
            for (key, value) in TEST_SALE.items():  # Make sure all fields are stored correctly
                assert sale.__getattribute__(key) == value
            assert sale.id == 1  # The ID autoincrements, starting at 1
            assert sale.status == Sale.STATUS_NOT_POSTED  # Test the status
            assert sale.api_id is None and sale.api_created is None and sale.error_msg is None  # Test None fields

    def test_create_sale_existing(self, test_app):
        with test_app.app_context():
            sale1 = SaleDB.create(**TEST_SALE)
            sale2 = SaleDB.create(**TEST_SALE)  # This should create a new sale, not update the current one
            assert sale1 is not sale2
            assert sale1.id == 1  # The ID autoincrements, starting at 1
            assert sale2.id == 2  # Next ID must be 2

    def test_sale_list_all(self, test_app):
        with test_app.app_context():
            sale1 = SaleDB.create(**TEST_SALE)
            sale2 = SaleDB.create(**TEST_SALE)  # This should create a new sale, not update the current one
            sale_list = SaleDB.list_all()
            assert len(sale_list) == 2
            assert sale_list[0] is sale1 and sale_list[1] is sale2

    def test_get_sale(self, test_app):
        with test_app.app_context():
            sale = SaleDB.get(1)  # This sale does not exist so this shoudl return None
            assert sale is None

            sale = SaleDB.create(**TEST_SALE)
            gotten_sale = SaleDB.get(sale.id)
            assert sale is gotten_sale

    def test_sale_get_by_user_id(self, test_app):
        with test_app.app_context():
            sale1 = SaleDB.create(**TEST_SALE)
            sale2 = SaleDB.create(**TEST_SALE_2)
            sale3 = SaleDB.create(**TEST_SALE)  # This should create a new sale, not update the first one

            sale_list = SaleDB.get_by_user_id(TEST_SALE['user_id'])
            assert len(sale_list) == 2
            assert sale_list[0] is sale1 and sale_list[1] is sale3
            assert sale2 not in sale_list

    def test_sale_get_by_item_id(self, test_app):
        with test_app.app_context():
            sale1 = SaleDB.create(**TEST_SALE)
            sale2 = SaleDB.create(**TEST_SALE_2)
            sale3 = SaleDB.create(**TEST_SALE)  # This should create a new sale, not update the first one

            sale_list = SaleDB.get_by_item_id(TEST_SALE['item_id'])
            assert len(sale_list) == 2
            assert sale_list[0] is sale1 and sale_list[1] is sale3
            assert sale2 not in sale_list

    def test_sale_delete(self, test_app):
        with test_app.app_context():
            sale = SaleDB.create(**TEST_SALE)
            assert len(SaleDB.list_all()) == 1

            deleted_sale = SaleDB.delete(sale.id)
            assert len(SaleDB.list_all()) == 0
            assert sale is deleted_sale


class TestSaleAPI:

    def test_post_sale(self, test_app):
        with test_app.app_context():
            sale = SaleDB.create(**TEST_SALE)
            SaleDB.post_sale(sale.id)

    def test_post_sale_incorrect_user(self, test_app):
        with test_app.app_context():
            sale = SaleDB.create(**TEST_SALE)
            SaleDB.update(id=sale.id, user_id=0)  # Set to nonexistent user id
            with pytest.raises(api.HTTPError) as err:
                SaleDB.post_sale(sale.id)
            assert '404' in str(err.value)
            assert sale.status == Sale.STATUS_HTTP_ERROR
            assert str(err.value) == sale.error_msg

    def test_post_sale_incorrect_item(self, test_app):
        with test_app.app_context():
            sale = SaleDB.create(**TEST_SALE)
            SaleDB.update(id=sale.id, item_id=1)  # Set to nonexistent item id
            with pytest.raises(api.HTTPError) as err:
                SaleDB.post_sale(sale.id)
            assert '404' in str(err.value)
            assert sale.status == Sale.STATUS_HTTP_ERROR
            assert str(err.value) == sale.error_msg

    def test_post_sale_no_sdd(self, test_app):
        with test_app.app_context():
            sale = SaleDB.create(**TEST_SALE)
            SaleDB.update(id=sale.id, user_id=TEST_USER_NO_SDD['id'])  # Set to no sdd user id
            with pytest.raises(api.UserNotSignedException) as err:
                SaleDB.post_sale(sale.id)
            assert '403' in str(err.value) and 'mandate' in str(err.value)
            assert sale.status == Sale.STATUS_SDD_NOT_SIGNED
            assert str(err.value) == sale.error_msg

    def test_post_sale_timeout(self, test_app):
        with test_app.app_context():
            with test_app.app_context():
                sale = SaleDB.create(**TEST_SALE)
                with pytest.raises(api.Timeout) as err:
                    SaleDB.post_sale(sale.id, timeout=0.001)
                assert sale.status == Sale.STATUS_TIMEOUT
                assert str(err.value) == sale.error_msg

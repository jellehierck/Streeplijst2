import pytest
from requests.exceptions import HTTPError, Timeout

from streeplijst2.config import TEST_ITEM, TEST_USER, TEST_USER_NO_SDD, TEST_FOLDER_ID
from streeplijst2.database import LocalDBController as db_controller
from streeplijst2.streeplijst import Sale
from streeplijst2.api import UserNotSignedException


def test_folder_get_item(test_app):
    with test_app.app_context():
        folder = db_controller.create_folder(folder_id=TEST_FOLDER_ID)
        assert folder.get_item(item_id=TEST_ITEM['id'])
        assert not folder.get_item(item_id=1)


def test_sale_post_sale(test_app):
    with test_app.app_context():
        item = db_controller.create_item(item_id=TEST_ITEM['id'])  # Load the test item
        user = db_controller.create_user(TEST_USER['s_number'])  # Load the test user

        sale = Sale(user, item, 1)  # Create a single sale of the test item
        response = sale.post_sale()

        assert response is not None


def test_sale_post_sale_errors(test_app):
    with test_app.app_context():
        item = db_controller.create_item(item_id=TEST_ITEM['id'])  # Load the test item
        user = db_controller.create_user(TEST_USER['s_number'])  # Load the test user
        no_sdd_user = db_controller.create_user(TEST_USER_NO_SDD['s_number'])  # Load the user without SDD mandate

        # Incorrect user
        with pytest.raises(HTTPError) as err:
            user.id = 0  # Set the user ID to a false value
            sale = Sale(user, item, 1)
            res = sale.post_sale()
        assert '404' in str(err.value)
        user.id = TEST_USER['id']  # Set the user ID back to the correct value

        # Incorrect item
        with pytest.raises(HTTPError) as err:
            item.id = 1  # Set the item ID to a false value
            sale = Sale(user, item, 1)
            res = sale.post_sale()
        assert '404' in str(err.value)
        item.id = TEST_ITEM['id']  # Set the item ID back to the correct value

        # No SDD sign on user
        with pytest.raises(UserNotSignedException) as err:
            sale = Sale(no_sdd_user, item, 1)
            res = sale.post_sale()
        assert str(403) in str(err.value) and 'mandate' in str(err.value)

        # Timeout
        with pytest.raises(Timeout) as err:
            sale = Sale(user, item, 1)
            res = sale.post_sale(timeout=0.001)

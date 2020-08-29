from streeplijst2.database import db_session

from streeplijst2.flask_app import create_app
from streeplijst2.streeplijst import User, Folder, Sale
from streeplijst2.config import TEST_USER, TEST_ITEM, TEST_FOLDER_NAME


def test_config():
    """Test create_app without passing test config."""
    assert not create_app().testing
    assert create_app({"TESTING": True}).testing


def test_hello(client):
    response = client.get("/hello")
    assert response.data == b"Hello, World!"


def test_database(app):  # TODO: Move those tests to test_streeplijst.py and/or test_database.py
    folder = Folder.from_config(TEST_FOLDER_NAME)
    item = folder.items[TEST_ITEM["id"]]
    user = User.from_api(TEST_USER["s_number"])
    sale = Sale(user, item, 1)

    s = db_session()
    s.add(folder)
    s.add(item)
    s.add(user)
    s.add(sale)

    s.commit()
    s.close()

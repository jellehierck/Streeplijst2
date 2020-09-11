from streeplijst2 import create_app
from streeplijst2.streeplijst import User, Folder, Sale
from streeplijst2.config import TEST_USER, TEST_ITEM, TEST_FOLDER_NAME


def test_config(test_app, db_uri_string):
    """Test create_app without passing test config."""
    assert not create_app({'SQLALCHEMY_DATABASE_URI': 'sqlite:///' + db_uri_string}).testing
    assert test_app.testing


def test_hello(client):
    response = client.get("/streeplijst/hello")
    assert response.data == b"Hello, World!"

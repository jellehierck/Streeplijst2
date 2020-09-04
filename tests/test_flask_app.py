from streeplijst2 import create_app
from streeplijst2.streeplijst import User, Folder, Sale
from streeplijst2.config import TEST_USER, TEST_ITEM, TEST_FOLDER_NAME


def test_config():
    """Test create_app without passing test config."""
    assert not create_app().testing
    assert create_app({"TESTING": True}).testing


def test_hello(client):
    response = client.get("/hello")
    assert response.data == b"Hello, World!"

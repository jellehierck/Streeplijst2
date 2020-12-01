from streeplijst2 import create_app


def test_config(test_app, db_uri_string):
    """Test create_app without passing test config."""
    assert not create_app({'SQLALCHEMY_DATABASE_URI': 'sqlite:///' + db_uri_string, 'DISABLE_LOGGING': True}).testing
    assert test_app.testing


def test_hello(client):
    response = client.get("/hello")
    assert response.data == b"Hello, World!"

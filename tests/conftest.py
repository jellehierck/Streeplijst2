import pytest

from streeplijst2 import create_app


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app({'TESTING': True})  # Create the app in testing mode.

    yield app  # app is yielded instead of returned to allow closing any other connections after this line.
    # If any connections need to be closed they go below this line


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

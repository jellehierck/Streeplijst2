import os

import pytest

from streeplijst2 import create_app


@pytest.fixture(scope="module")
def script_loc(request):
    """Return the directory of the currently running test script. Source:
    https://stackoverflow.com/questions/34504757/get-pytest-to-look-within-the-base-directory-of-the-testing-script"""
    return request.fspath.join('..')


@pytest.fixture(scope="module")
def db_uri_string(script_loc):
    """Return the string representation of the sqlite database URI."""
    return str(script_loc) + '/test.db'


@pytest.fixture
def test_app(script_loc, db_uri_string):
    """Create and configure a new app instance for each test."""
    test_app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///' + db_uri_string  # Store test db in test directory
    })  # Create the app in testing mode.

    yield test_app  # app is yielded instead of returned to allow closing any other connections after this line.

    # If any connections need to be closed they go below this line
    os.remove(db_uri_string)  # Remove the temporary database file


@pytest.fixture
def client(test_app):
    """A test client for the app."""
    return test_app.test_client()


@pytest.fixture
def runner(test_app):
    """A test runner for the app's Click commands."""
    return test_app.test_cli_runner()

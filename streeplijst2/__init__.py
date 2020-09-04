"""
flask_app.py

Contains all Flask logic to connect this Python backend to the HTML frontend.
"""
import os
from flask import Flask
from flask_caching import Cache

from streeplijst2.streeplijst import User, Folder
from credentials import DEV_KEY  # TODO: Remove this line and replace with decent call to config file


def create_app(config=None):
    """
    Flask app factory function.

    :param config: The configuration to load
    :return: Flask app instance
    """
    app = Flask(__name__, instance_relative_config=True)  # Create the app

    from streeplijst2.database import SQLALCHEMY_DATABASE_URL
    app.config.from_mapping(  # TODO: Change this so that it imports from a config file
            SECRET_KEY=DEV_KEY,  # TODO: change this key
            DATABASE=SQLALCHEMY_DATABASE_URL,
            CACHE_TYPE='simple'  # Caching for temporarily storing results of time-consuming requests (e.g. get folders)
    )

    # Load configuration
    if config is None:
        # load the instance config, if it exists, when not testing
        # app.config.from_pyfile('config.py', silent=True) # TODO: Actually import from a config file
        pass
    else:
        # load the test config if passed in
        app.config.from_mapping(config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Set up the database
    from streeplijst2.database import db  # Import the database module
    db.init_app(app)  # Define the database tables and models

    # Set up caching
    cache = Cache(app)

    # Register all routes
    from streeplijst2.routes import register_routes
    register_routes(app, cache)

    return app

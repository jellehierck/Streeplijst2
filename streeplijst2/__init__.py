"""
Contains all Flask logic to connect this Python backend to the HTML frontend.
"""
import os
from flask import Flask

from streeplijst2.config import DEV_KEY  # TODO: Remove this line and replace with decent call to config file


def create_app(config=None):
    """
    Flask app factory function.

    :param config: The configuration to load
    :return: Flask app instance
    """
    app = Flask(__name__, instance_relative_config=True)  # Create the app

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.config.from_mapping(  # TODO: Change this so that it imports from a config file
        SECRET_KEY=DEV_KEY,  # TODO: change this key
        SQLALCHEMY_DATABASE_URI='sqlite:///' + app.instance_path + '/database.sqlite',  # Database in instance folder
        SQLALCHEMY_TRACK_MODIFICATIONS=False  # Reduces the overhead of track_modifications
    )

    # Load configuration
    if config is None:
        # load the instance config, if it exists, when not testing
        # app.config.from_pyfile('config.py', silent=True) # TODO: Actually import from a config file
        pass
    else:
        # load the test config if passed in
        app.config.from_mapping(config)

    # Set up the database
    from streeplijst2.extensions import db  # Import the database module
    db.init_app(app)  # Define the database tables and models
    with app.app_context():
        db.create_all()

    # Set up caching
    from streeplijst2.extensions import cache
    cache.init_app(app)

    # Register all routes
    from streeplijst2.routes import home, streeplijst
    app.register_blueprint(home)
    app.register_blueprint(streeplijst)

    return app

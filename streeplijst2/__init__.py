"""
flask_app.py

Contains all Flask logic to connect this Python backend to the HTML frontend.
"""
import os
from flask import Flask

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
            DATABASE=SQLALCHEMY_DATABASE_URL
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
    from streeplijst2.database import init_db, db_session  # Import the database module
    init_db()  # Define the database tables and models

    @app.teardown_appcontext  # Close and remove database sessions when the application shuts down
    def shutdown_session(exception=None):
        db_session.remove()

    # Register all routes
    from streeplijst2.routes import bp
    app.register_blueprint(bp)

    return app

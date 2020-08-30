"""
flask_app.py

Contains all Flask logic to connect this Python backend to the HTML frontend.
"""
import os
from flask import Flask, render_template, redirect, url_for, request, flash

from streeplijst2.streeplijst import User, Folder
from credentials import DEV_KEY  # TODO: Remove this line and replace with decent call to config file


def create_app(config=None):
    """
    Flask app factory function.

    :param config: The configuration to load
    :return: Flask app instance
    """
    app = Flask(__name__, instance_relative_config=True)  # Create the app
    app.config.from_mapping(  # TODO: Change this so that it imports from a config file
            SECRET_KEY=DEV_KEY  # TODO: change this key
    )

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

    # Close and remove database sessions at the end of a request or when the application shuts down
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    # Hello world response
    @app.route('/hello')
    def hello():
        return "Hello, World!"

    # Landing page
    @app.route('/')
    def index():
        return redirect(url_for('login'))

    # Login page. When called with GET, this loads the login screen. When called with POST, attempts to login user.
    @app.route('/login', methods=('GET', 'POST'))
    def login():
        if request.method == 'GET':  # Load the login page to let users enter their s-number
            return render_template('login.html')

        elif request.method == 'POST':  # Attempt to login the user
            s_number = request.form['student-number']  # Load the student number from the push form
            user = User.from_api(s_number)  # Create a User
            flash(user.first_name)  # Display the name as temporary measure
            return redirect(url_for('folders_home'))  # Redirect to the same page as temporary measure

    # Folders home page. Displays all folders to choose products from.
    @app.route('/folders')
    @app.route('/folders/home')
    def folders_home():
        folders = Folder.all_folders_from_config()  # Load all folders
        # TODO: Do not call this method on endpoint loading but periodically (saves loading time).
        return render_template('folders_home.html', folders=folders)

    # Specific folder pages. Displays all products in the specified folder.
    @app.route('/folders/<int:folder_id>')
    def folder(folder_id):
        return render_template('folder.html', items=None)

    return app

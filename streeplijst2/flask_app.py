"""
flask_app.py

Contains all Flask logic to connect this Python backend to the HTML frontend.
"""
import os
from flask import Flask, render_template, redirect, url_for, request, flash

import streeplijst2.streeplijst as streeplijst
from credentials import DEV_KEY


def create_app(test_config=None):
    app = Flask(__name__)  # Create the app

    app.config.from_mapping(
            SECRET_KEY=DEV_KEY,  # Secret key required by Flask to make POST requests.
    )

    if test_config is None:  # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)  # TODO: Add lines to config.py
    else:  # load the test config if passed in
        app.config.update(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

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
            user = streeplijst.User(s_number)  # Create a User
            flash(user.first_name)  # Display the name as temporary measure
            return redirect(url_for('folders_home'))  # Redirect to the same page as temporary measure

    # Folders home page. Displays all folders to choose products from.
    @app.route('/folders')
    @app.route('/folders/home')
    def folders_home():
        folders = streeplijst.get_all_folders_from_config()  # Load all folders
        # TODO: Do not call this method on endpoint loading but periodically (saves loading time).
        return render_template('folders_home.html', folders=folders)

    # Specific folder pages. Displays all products in the specified folder.
    @app.route('/folders/<int:folder_id>')
    def folder(folder_id):
        return render_template('folder.html', items=None)

    return app


# TODO: Remove the below section as it is only used for development testing.
# Tests various API calls and streeplijst.py module interactions.
if __name__ == "__main__":
    folder_speciaal = streeplijst.get_folder_from_config("Speciaal")
    # folders = items.get_all_folders_from_config()
    user = streeplijst.User("s9999999")

    item = folder_speciaal.items[13591]
    sale = streeplijst.Sale(user, item, 1)
    sale.post_sale()

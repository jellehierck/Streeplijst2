"""
app.py

Contains all Flask logic to connect this Python backend to the HTML frontend.
"""
import datetime
from flask import Flask, render_template, redirect, url_for, request, flash

import streeplijst2.streeplijst as streeplijst
import streeplijst2.api as api
from credentials import DEV_KEY, SECRET_KEY


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
            SECRET_KEY=DEV_KEY,
    )

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
            s_number = request.form['student-number']
            user = streeplijst.User(s_number)
            flash(user.first_name)
            return redirect(url_for('login'))



    @app.route('/time')
    def get_current_time():
        return {'time': datetime.datetime.now().isoformat()}

    return app


if __name__ == "__main__":
    folder_speciaal = streeplijst.get_folder_from_config("Speciaal")
    # folders = items.get_all_folders_from_config()
    user = streeplijst.User("s9999999")

    item = folder_speciaal.items[13591]
    sale = streeplijst.Sale(user, item, 1)
    sale.submit_sale()

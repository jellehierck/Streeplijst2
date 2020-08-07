"""
app.py

Contains all Flask logic to connect this Python backend to the HTML frontend.
"""
import datetime
from flask import Flask, render_template, redirect, url_for

import streeplijst2.streeplijst as streeplijst
import streeplijst2.api as api


def create_app(test_config=None):
    app = Flask(__name__)

    # Initial page loaded on startup
    @app.route('/')
    def index():
        return redirect(url_for('login_page'))  # Redirects to the login page by default

    # Login page
    @app.route('/login_page')
    def login():
        return render_template("login_page.html")  # Render the Jinja HTML template for login

    return app


if __name__ == "__main__":
    folder_speciaal = streeplijst.get_folder_from_config("Speciaal")
    # folders = items.get_all_folders_from_config()
    user = streeplijst.User("s9999999")

    item = folder_speciaal.items[13591]
    sale = streeplijst.Sale(user, item, 1)
    sale.submit_sale()

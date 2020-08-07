"""
app.py

Contains all Flask logic to connect this Python backend to the ReactJS frontend.
"""
import datetime
from flask import Flask

import streeplijst2.streeplijst as streeplijst
import streeplijst2.api as api


def create_app(test_config=None):
    app = Flask(__name__)

    @app.route('/')
    def index():
        return "<h1>Streeplijst</h1>"

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

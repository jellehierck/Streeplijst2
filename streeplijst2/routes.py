from flask import redirect, url_for, render_template, request, flash, session, jsonify, Blueprint

from requests.exceptions import HTTPError, Timeout

from streeplijst2.streeplijst import User, Folder, Item
from streeplijst2.database import LocalDBController as db_controller
from streeplijst2.api import UserNotFoundException
from streeplijst2.extensions import cache

home = Blueprint('home', __name__)


# Hello world response as test message
@home.route('/hello')
def hello():
    return "Hello, World!"


# Landing page
@home.route('/')
@home.route('/home')
def index():
    # return redirect(url_for('streeplijst.streeplijst_home'))  # TODO: Remove this temporary testing route
    return redirect(url_for('home.login'))


# Login page. When called with GET, this loads the login screen. When called with POST, attempts to login user.
@home.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'GET':  # Load the login page to let users enter their s-number
        flash('Welkom')
        flash('Leuk dat je er bent')
        flash('404 Client Error: User was not found for URL www.url.com/really/really/long/url/with/lots/of/slashes', 'error')
        return render_template('login.jinja2')

    elif request.method == 'POST':  # Attempt to login the user
        s_number = request.form['s-number']  # Load the student number from the push form
        try:  # Attempt to find the user from Congressus
            user = db_controller.get_or_create_user(s_number=s_number)  # Create a User
        except UserNotFoundException as err:  # The user was not found
            flash(str(err))  # TODO: Properly handle this exception
            return render_template('login.html')
        except (HTTPError, Timeout) as err:  # There was a connection error
            flash(str(err))  # TODO: Properly handle this exception
            return render_template('login.html')

        session['user_id'] = user.id
        flash(user.first_name)  # Display the name as temporary measure TODO: replace this line
        return redirect(url_for('streeplijst.folder', folder_id=1996))  # Redirect to the streeplijst


@home.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key, None)  # Remove all items from the session
    flash('Logged out.')
    return redirect(url_for('home.login'))


###################################
# Streeplijst specific blueprints #
###################################

streeplijst = Blueprint('streeplijst', __name__, url_prefix='/streeplijst')


@streeplijst.route('/')
def streeplijst_home():
    return redirect(url_for('streeplijst.folders_main'))

    if 'user' in session and session['user']:  # If there is a user logged in
        return redirect(url_for('streeplijst.folders_main'))  # TODO: Add a redirect to the home view for streeplijst
    else:  # If no user is logged in
        return redirect(url_for('home'))


@streeplijst.route('/sale', methods=['POST'])
def sale():
    print(request.form['item-id'])
    print(request.form['quantity'])
    return jsonify({'response': 'success'})


# Folders home page. Displays all folders to choose products from.
@streeplijst.route('/folders/main')
# @cache.cached(timeout=60)  # Set the timeout for folders at 60 seconds. TODO: Do not hard code this value
def folders_main():
    folder = db_controller.get_or_create_folder(folder_id=1996, sync=True, force_sync=True, auto_commit=True)
    # folder = Folder.from_config(folder_name="Koek")
    return render_template('items.jinja2', folder_items=folder.items)  # TODO: Remove this temporary testing route

    if 'user' in session:
        folder = Folder.from_config(folder_name="Koek")
        return render_template('items.jinja2', folder_items=folder.items)
    else:
        flash('Log in to see folders')  # Remove this temporary placeholder message
        return redirect(url_for('login'))


# Specific folder pages. Displays all products in the specified folder.
@streeplijst.route('/folder/<int:folder_id>')
def folder(folder_id):
    folder = db_controller.get_or_create_folder(folder_id=folder_id, sync=True, force_sync=True, auto_commit=True)
    return render_template('items.jinja2', folder_items=folder.items)  # TODO: Remove this temporary testing route

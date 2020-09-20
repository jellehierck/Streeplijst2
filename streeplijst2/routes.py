from flask import redirect, url_for, render_template, request, flash, session, jsonify, Blueprint

from requests.exceptions import HTTPError, Timeout

from streeplijst2.config import TEST_FOLDER_ID, FOLDERS
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
    return redirect(url_for('home.login'))


# Login page. When called with GET, this loads the login screen. When called with POST, attempts to login user.
@home.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'GET':  # Load the login page to let users enter their s-number
        return render_template('login.jinja2')

    elif request.method == 'POST':  # Attempt to login the user
        s_number = request.form['s-number']  # Load the student number from the push form
        try:  # Attempt to find the user from Congressus
            user = db_controller.get_or_create_user(s_number=s_number)  # Create a User
        except UserNotFoundException as err:  # The user was not found
            flash('Gebruiker ' + s_number + ' is niet gevonden. Probeer het opnieuw.', 'error')
            return render_template('login.jinja2')
        except HTTPError as err:  # There was a connection error
            flash(str(err), 'error')
            return render_template('login.jinja2')

        # Add session variables to identify the user
        session['user_id'] = user.id
        session['user_first_name'] = user.first_name
        session['user_s_number'] = user.s_number

        return redirect(url_for('streeplijst.folder'))  # Redirect to the streeplijst


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
    if 'user_id' in session:
        return redirect(url_for('streeplijst.folders_main'))
    else:
        pass

    if 'user' in session and session['user']:  # If there is a user logged in
        return redirect(url_for('streeplijst.folders_main'))  # TODO: Add a redirect to the home view for streeplijst
    else:  # If no user is logged in
        return redirect(url_for('home'))


@streeplijst.route('/sale', methods=['POST'])
def sale():
    print(request.form['item-id'])
    print(request.form['quantity'])
    return jsonify({'response': 'success, but sale is not posted because of testing.'})


# Folder contents
@streeplijst.route('/folder')
@streeplijst.route('/folder/<int:folder_id>')
def folder(folder_id=TEST_FOLDER_ID):  # TODO: Change default folder to a more useful folder.
    if 'user_id' in session:
        folder = db_controller.get_or_create_folder(folder_id=folder_id, sync=True, force_sync=False, auto_commit=True)
        return render_template('folder.jinja2', meta_folders=FOLDERS, folder_items=folder.items)

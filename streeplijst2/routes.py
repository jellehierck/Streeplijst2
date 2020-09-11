from flask import redirect, url_for, render_template, request, flash, session, jsonify, Blueprint

from requests.exceptions import HTTPError, Timeout

from streeplijst2.streeplijst import User, Folder, Item
from streeplijst2.api import UserNotFoundException
from streeplijst2.cache import cache

bp = Blueprint('streeplijst', __name__, url_prefix='/streeplijst')


# Hello world response as test message
@bp.route('/hello')
def hello():
    return "Hello, World!"


# Landing page
@bp.route('/')
def index():
    folder = Folder.from_config(folder_name="Koek")
    print(folder.items)
    # test_item = Item('Testproduct', 13591, 0, None, None, True)
    return render_template('items.jinja2', folder_items=folder.items)  # TODO: Remove this temporary testing route
    # return redirect(url_for('login'))


@bp.route('/sale', methods=['POST'])
def sale():
    print(request.form['item-id'])
    print(request.form['quantity'])
    return jsonify({'response': 'success'})


# Login page. When called with GET, this loads the login screen. When called with POST, attempts to login user.
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'GET':  # Load the login page to let users enter their s-number
        return render_template('login.html')

    elif request.method == 'POST':  # Attempt to login the user
        s_number = request.form['student-number']  # Load the student number from the push form
        try:  # Attempt to find the user from Congressus
            user = User.from_api(s_number)  # Create a User
        except UserNotFoundException as err:  # The user was not found
            flash(str(err))  # TODO: Properly handle this exception
            return render_template('login.html')
        except (HTTPError, Timeout) as err:  # There was a connection error
            flash(str(err))  # TODO: Properly handle this exception
            return render_template('login.html')

        session['user_id'] = user.id
        flash(user.first_name)  # Display the name as temporary measure TODO: replace this line
        return redirect(url_for('folders_main'))  # Redirect to the folders page


@bp.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key, None)  # Remove all items from the session
    flash('Logged out.')
    return redirect(url_for('login'))


# Folders home page. Displays all folders to choose products from.
@bp.route('/folders/main')
@cache.cached(timeout=60)  # Set the timeout for folders at 60 seconds. TODO: Do not hard code this value
def folders_main():
    if 'user' in session:
        folders = Folder.all_folders_from_config()  # Load all folders
        # TODO: Do not call this method on endpoint loading but periodically (saves loading time).
        return render_template('folders_main.html', folders=folders)
    else:
        flash('Log in to see folders')  # Remove this temporary placeholder message
        return redirect(url_for('login'))


# Specific folder pages. Displays all products in the specified folder.
@bp.route('/folders/<int:folder_id>')
def folder(folder_id):
    return render_template('folder.html', items=None)

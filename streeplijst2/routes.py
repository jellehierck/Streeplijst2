from flask import redirect, url_for, render_template, request, flash, session, Blueprint

from requests.exceptions import HTTPError
from functools import wraps  # Used in the login_required decorator function

from streeplijst2.database import DBController as db_controller
from streeplijst2.api import UserNotFoundException


def login_required(func):
    """
    Decorator function: Redirects the user to the login page if they are not logged in. Based on
    https://realpython.com/primer-on-python-decorators/#is-the-user-logged-in.

    :param func: Function to be decorated
    :return: A redirect to home.login if there is no user currently logged in.
    """
    @wraps(func)  # functools wrapper used to preserve function information between calls (best practise for decorators)
    def wrapper_login_required(*args, **kwargs):
        if 'user_id' not in session:  # If there is no user logged in, redirect them to the login page
            return redirect(url_for("home.login"))
        return func(*args, **kwargs)  # If a user is logged in, execute the function normally

    return wrapper_login_required


##################
# Home blueprint #
##################

bp_home = Blueprint('home', __name__)


# Hello world response as test message
@bp_home.route('/hello')
def hello():
    return "Hello, World!"


# Hello world response as test message for logged in users
@bp_home.route('/secret_hello')
@login_required
def secret_hello():
    return "Hello, Secret World!"


# Landing page
@bp_home.route('/')
@bp_home.route('/home')
@bp_home.route('/index')
def index():
    return redirect(url_for('home.login'))


# Login page. When called with GET, this loads the login screen. When called with POST, attempts to login user.
@bp_home.route('/login', methods=('GET', 'POST'))
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


@bp_home.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key, None)  # Remove all items from the session (user data)
    flash('Uitgelogd.')  # TODO: Add temporary messages which disappear after a time.
    return redirect(url_for('home.login'))

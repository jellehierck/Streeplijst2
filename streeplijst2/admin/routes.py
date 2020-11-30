from flask import Blueprint, session, redirect, url_for, request, render_template
from functools import wraps  # Used in decorator function
from flask_login import login_required as admin_login_required


def check_admin_logged_in(func):
    """
    Decorator function: Redirects the user to the home page if there is no admin logged in. Based on
    https://realpython.com/primer-on-python-decorators/#is-the-user-logged-in.

    :param func: Function to be decorated
    :return: A redirect to home.index if there is no user currently logged in. Otherwise, func executes regularly
    """

    @wraps(func)  # functools wrapper used to preserve function information between calls (best practise for decorators)
    def wrapper_login_required(*args, **kwargs):
        if 'admin_id' not in session:  # If there is no admin logged in, redirect them to the home page
            return redirect(url_for("home.index"))
        return func(*args, **kwargs)  # If an admin is logged in, execute the function normally

    return wrapper_login_required


def admin_logout():
    """Log out an admin by clearing all admin fields in the session data."""
    session.pop('admin_id', None)
    session.pop('admin_name', None)


###################
# Admin blueprint #
###################

bp_admin = Blueprint('admin', __name__, url_prefix='/admin')


@bp_admin.route('/')
@bp_admin.route('/home')
@bp_admin.route('/index')
def index():
    """Default page for admin view."""
    return redirect(url_for('admin.login'))


@bp_admin.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'GET':
        admin_logout()  # If this page is accessed with GET, no admin must be logged in so clear the current admin
        return render_template('admin/login_admin.jinja2')

    elif request.method == 'POST':
        admin_code = request.form['admin-code']
        # TODO: Add a hasing decoder here


@bp_admin.route('/sales')
@admin_login_required
def sales_view():
    return "Sales View"

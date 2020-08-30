from flask import Blueprint, redirect, url_for, render_template, request, flash
from streeplijst2.streeplijst import User, Folder

bp = Blueprint('streeplijst', __name__)


# Hello world response as test message
@bp.route('/hello')
def hello():
    return "Hello, World!"


# Landing page
@bp.route('/')
def index():
    return redirect(url_for('login'))


# Login page. When called with GET, this loads the login screen. When called with POST, attempts to login user.
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'GET':  # Load the login page to let users enter their s-number
        return render_template('login.html')

    elif request.method == 'POST':  # Attempt to login the user
        s_number = request.form['student-number']  # Load the student number from the push form
        user = User.from_api(s_number)  # Create a User
        flash(user.first_name)  # Display the name as temporary measure
        return redirect(url_for('folders_home'))  # Redirect to the same page as temporary measure


# Folders home page. Displays all folders to choose products from.
@bp.route('/folders')
@bp.route('/folders/home')
def folders_home():
    folders = Folder.all_folders_from_config()  # Load all folders
    # TODO: Do not call this method on endpoint loading but periodically (saves loading time).
    return render_template('folders_home.html', folders=folders)


# Specific folder pages. Displays all products in the specified folder.
@bp.route('/folders/<int:folder_id>')
def folder(folder_id):
    return render_template('folder.html', items=None)

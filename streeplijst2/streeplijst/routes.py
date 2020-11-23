from flask import redirect, url_for, render_template, flash, session, Blueprint, request

from streeplijst2.config import FOLDERS_META, TEST_FOLDER_ID
from streeplijst2.routes import login_required
from streeplijst2.streeplijst.database import FolderDB, SaleDB, ItemDB, UserDB
from streeplijst2.exceptions import Streeplijst2Warning, Streeplijst2Exception, HTTPError, Timeout

bp_streeplijst = Blueprint('streeplijst', __name__, url_prefix='/streeplijst')


@bp_streeplijst.context_processor
def meta_folders_injector():
    """
    Inject the meta folders for the display of folders at the top of the screen. This function makes sure that every
    page registered to the streeplijst blueprint will include the folder meta.
    """
    return dict(folders_meta=FOLDERS_META)


###############################
# Streeplijst specific routes #
###############################

@bp_streeplijst.route('/')  # This is the default page of /streeplijst
@bp_streeplijst.route('/index')  # This is the default page of /streeplijst
@bp_streeplijst.route('/home')  # This is the default page of /streeplijst
@login_required  # First check if the user is logged in.
def index():
    """Default page."""
    return redirect(url_for('streeplijst.folder'))


@bp_streeplijst.route('/folder')  # If no folder_id is specified, the default folder is loaded
@bp_streeplijst.route('/folder/<int:folder_id>')  # When a folder is specified it is loaded
@login_required
def folder(folder_id=TEST_FOLDER_ID):  # TODO: Change default folder to a more useful folder.
    """
    Loads the view of a specific folder.

    :param folder_id: The folder ID to display.
    """
    if 'user_id' in session:
        session['last_folder_id'] = folder_id  # Store what was the last folder this user accessed in the cookie
        folder = FolderDB.load_folder(folder_id=folder_id)
        items = FolderDB.get_items_in_folder(id=folder_id)
        return render_template('streeplijst/folder.jinja2', folder=folder, items=items)
    else:
        flash('Log in first.', 'message')
        return redirect(url_for('home.login'))


@bp_streeplijst.route('/sale', methods=['POST'])
@login_required
def sale():
    """Post a sale to the API."""
    quantity = int(request.form['quantity'])
    item_id = int(request.form['item-id'])
    user_id = session['user_id']

    # TEST PARAMETERS
    # quantity = 1
    # item_id = 13591
    # user_id = 347980

    try:  # Try creating the sale
        item = ItemDB.get(item_id)
        user = UserDB.get(user_id)
        sale = SaleDB.create_quick(quantity=quantity, item_id=item_id, user_id=user_id)
    except Streeplijst2Exception as err:  # There was an error which caused the database queries to fail
        flash(str(err), 'error')
        return folder(folder_id=session['last_folder_id'])

    try:
        sale = SaleDB.post_sale(sale.id)  # Post the sale
    except Streeplijst2Warning as err:  # If a warning occurred, only flash the warning but continue normally.
        flash(str(err))
        flash('Post was still successful.')
    except (Streeplijst2Exception, HTTPError, Timeout) as err:  # There was an error which caused the post to fail
        flash(str(err), 'error')
        flash('Please try again. If the problem persist, contact the board.')
        return folder(folder_id=session['last_folder_id'])

    return render_template('streeplijst/checkout.jinja2', sale=sale, item=item, user=user)

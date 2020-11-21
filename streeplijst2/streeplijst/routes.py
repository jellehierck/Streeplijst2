from flask import redirect, url_for, render_template, flash, session, Blueprint

from streeplijst2.config import FOLDERS, TEST_FOLDER_ID
from streeplijst2.routes import login_required
from streeplijst2.streeplijst.database import FolderDB, SaleDB, ItemDB, UserDB
from streeplijst2.exceptions import Streeplijst2Warning, Streeplijst2Exception

##################################
# Streeplijst specific blueprint #
##################################

bp_streeplijst = Blueprint('streeplijst', __name__, url_prefix='/streeplijst')


# Default page and folder contents
@bp_streeplijst.route('/')  # This is the default page of /streeplijst
@bp_streeplijst.route('/index')  # This is the default page of /streeplijst
@bp_streeplijst.route('/home')  # This is the default page of /streeplijst
@login_required  # First check if the user is logged in.
def index():
    return redirect(url_for('streeplijst.folder'))


@bp_streeplijst.route('/folder')  # If no folder_id is specified, the default folder is loaded
@bp_streeplijst.route('/folder/<int:folder_id>')  # When a folder is specified it is loaded
def folder(folder_id=TEST_FOLDER_ID):  # TODO: Change default folder to a more useful folder.
    if 'user_id' in session:
        loaded_folder = FolderDB.load_folder(folder_id=folder_id)
        meta_folders = FOLDERS  # The folder metas for all folders are loaded to display at top of the screen
        return render_template('folder.jinja2', meta_folders=meta_folders, folder=loaded_folder)
    else:
        flash('Log in first.', 'message')
        return redirect(url_for('home.login'))


@bp_streeplijst.route('/sale', methods=['POST'])
def sale():
    # quantity = request.form['quantity']
    # item_id = request.form['item-id']
    # user_id = session['user_id']

    # TODO: remove the following test parameters and uncomment the block above
    quantity = 1
    item_id = 13591
    user_id = 347980

    item = ItemDB.get(item_id)
    user = UserDB.get(user_id)
    sale = SaleDB.create_quick(quantity=quantity, item_id=item_id, user_id=user_id)

    try:
        sale = SaleDB.post_sale(sale.id)
    except Streeplijst2Warning as err:
        flash(str(err))

    meta_folders = FOLDERS  # The folder metas for all folders are loaded to display at top of the screen
    return render_template('checkout.jinja2', meta_folders=meta_folders, sale=sale, item=item, user=user)

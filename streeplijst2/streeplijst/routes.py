from flask import redirect, url_for, render_template, request, flash, session, jsonify, Blueprint

from streeplijst2.config import FOLDERS
from streeplijst2.streeplijst.database import StreeplijstDBController as db_controller

##################################
# Streeplijst specific blueprint #
##################################

bp_streeplijst = Blueprint('streeplijst', __name__, url_prefix='/streeplijst')


# Default page and folder contents
@bp_streeplijst.route('/')  # This is the default page of /streeplijst
@bp_streeplijst.route('/index')  # This is the default page of /streeplijst
@bp_streeplijst.route('/home')  # This is the default page of /streeplijst
def index():
    return redirect(url_for('streeplijst.folder'))


@bp_streeplijst.route('/folder')  # If no folder_id is specified, the default folder is loaded
@bp_streeplijst.route('/folder/<int:folder_id>')  # When a folder is specified it is loaded
def folder(folder_id=1998):  # TODO: Change default folder to a more useful folder.
    if 'user_id' in session:
        folder = db_controller.get_or_create_folder(folder_id=folder_id, sync=True, force_sync=False, auto_commit=True)
        meta_folders = FOLDERS  # The folder metas for all folders are loaded to display at top of the screen
        return render_template('folder.jinja2', meta_folders=meta_folders, folder=folder)
    else:
        flash('Log eerst in.', 'message')
        return redirect(url_for('home.login'))


@bp_streeplijst.route('/sale', methods=['POST', 'GET'])
def sale():
    # item_id = request.form['item-id']
    # quantity = request.form['quantity']
    # user_id = session['user_id']

    item_id = 13591
    quantity = 1
    user_id = 347980

    user = db_controller.get_or_create_user("s9999999", auto_commit=True)
    item = db_controller.get_or_create_folder(1998, sync=True, force_sync=True, auto_commit=True)

    sale = db_controller.create_sale(item_id=item_id, user_id=user_id, quantity=quantity, auto_commit=True)
    #   sale.post_sale()
    db_controller.commit()

    meta_folders = FOLDERS  # The folder metas for all folders are loaded to display at top of the screen
    return render_template('checkout.jinja2', meta_folders=meta_folders, sale=sale, item=sale.item, user=sale.user)
    # return jsonify({'response': 'success, but sale is not posted because of testing.'})

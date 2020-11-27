from flask import Flask


def init_app(app: Flask, config=None) -> None:
    """
    Set up all admin related stuff in the flask application factory.

    :param app: The flask app to initialize.
    """
    # Set up the admin environment
    from streeplijst2.extensions import admin_manager
    from streeplijst2.admin.database import AdminDB
    admin_manager.init_app(app)

    @admin_manager.user_loader
    def load_admin(admin_id):  # Function required for flask_login extension to load admins
        return AdminDB.get_by_id(int(admin_id))  # admin_id is converted to integer value

    from streeplijst2.admin.routes import bp_admin
    app.register_blueprint(bp_admin)

    admin_manager.login_view = bp_admin.name + '.login'  # This view is accessed when a non-admin accesses admin pages
    admin_manager.login_message = 'Deze pagina kan alleen bekeken worden als admin.'
    admin_manager.login_message_category = 'error'

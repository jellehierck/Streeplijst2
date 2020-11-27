from datetime import datetime
from flask_login import UserMixin

from streeplijst2.extensions import db


class Admin(db.Model, UserMixin):
    # Class attributes for SQLAlchemy
    __tablename__ = 'admins'

    # Table columns
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # ID
    username = db.Column(db.String, unique=True)  # Login name of this admin, usually student number
    name = db.Column(db.String)  # Name for displaying
    password_hash = db.Column(db.String)  # Hashed password
    last_accessed = db.Column(db.DateTime, nullable=True)  # Storing when an admin was last logged in
    active = db.Column(db.Boolean)  # Store whether the admin is active

    created = db.Column(db.DateTime)
    updated = db.Column(db.DateTime)

    def __init__(self, **kwargs) -> None:
        """
        Instantiates an Admin object.

        :param username: Admin username. Usually this is the student number.
        :param name: Admin name for displaying.
        :param password_hash: Hashed password.
        """
        super().__init__(**kwargs)
        self.created = datetime.now()
        self.updated = datetime.now()

    def is_active(self):
        """Overwritten function of flask-login."""
        return self.active

    def get_id(self):
        """Overwritten function of flask-login"""
        return self.id

    def __repr__(self):
        return '<Admin %s>' % self.name

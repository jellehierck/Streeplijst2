from datetime import datetime

from streeplijst2.extensions import db


class User(db.Model):
    # Class attributes for SQLAlchemy
    __tablename__ = 'user'

    # Table columns
    id = db.Column(db.Integer, primary_key=True)
    s_number = db.Column(db.String)
    first_name = db.Column(db.String)
    last_name_prefix = db.Column(db.String)
    last_name = db.Column(db.String)
    date_of_birth = db.Column(db.DateTime)
    has_sdd_mandate = db.Column(db.Boolean)
    profile_picture = db.Column(db.String)

    def __init__(self, s_number: str, id: int, date_of_birth: datetime, first_name: str, last_name: str,
                 last_name_prefix: str = '', has_sdd_mandate: bool = False, profile_picture: dict = ''):
        """
        Create a new User object.

        :param s_number: Student or Employee number (Congressus user name)
        :param id: Congressus user id
        :param date_of_birth: Date of Birth (ISO formatted datetime string)
        :param first_name: First Name
        :param last_name: Last Name
        :param last_name_prefix: Last Name Prefix
        :param has_sdd_mandate: Has this user signed their SDD mandate
        :param profile_picture: Dict with URL strings to profile pictures
        """
        self.s_number = s_number
        self.id = id
        self.first_name = first_name
        self.last_name_prefix = last_name_prefix
        self.last_name = last_name
        self.date_of_birth = date_of_birth
        self.has_sdd_mandate = has_sdd_mandate
        self.profile_picture = profile_picture

    def update(self, **kwargs):
        """
        Update this user's data fields.

        :param kwargs: The fields are updated with keyword arguments.
        """
        # If no kwarg is given for an attribute, set it to the already stored attribute
        self.s_number = kwargs.get('s_number', self.s_number)
        self.id = kwargs.get('id', self.id)
        self.first_name = kwargs.get('first_name', self.first_name)
        self.last_name_prefix = kwargs.get('last_name_prefix', self.last_name_prefix)
        self.last_name = kwargs.get('last_name', self.last_name)
        self.date_of_birth = kwargs.get('date_of_birth', self.date_of_birth)
        self.has_sdd_mandate = kwargs.get('has_sdd_mandate', self.has_sdd_mandate)
        self.profile_picture = kwargs.get('profile_picture', self.profile_picture)

from datetime import datetime, date

from streeplijst2.extensions import db


class User(db.Model):
    # Class attributes for SQLAlchemy
    __tablename__ = 'users'

    # Table columns
    id = db.Column(db.Integer, primary_key=True)
    s_number = db.Column(db.String)
    first_name = db.Column(db.String)
    last_name_prefix = db.Column(db.String, nullable=True)
    last_name = db.Column(db.String)
    date_of_birth = db.Column(db.DateTime)
    has_sdd_mandate = db.Column(db.Boolean)
    profile_picture = db.Column(db.String, nullable=True)

    created = db.Column(db.DateTime)
    updated = db.Column(db.DateTime)

    def __init__(self, **kwargs) -> None:
        """
        Instantiates a User object.

        :param id: Congressus user id.
        :param s_number: Student or Employee number (Congressus user name)
        :param first_name: First name.
        :param last_name: Last name.
        :param date_of_birth: Date of birth.
        :param last_name_prefix: Last name prefix (e.g. 'van der').
        :param has_sdd_mandate: Flag whether this user has signed their SDD mandate (required for making any purchase).
        :param profile_picture: URL to profile picture.
        """
        super().__init__(**kwargs)
        self.created = datetime.now()
        self.updated = datetime.now()

    def __repr__(self):
        return '<User %s>' % self.s_number

# class User(db.Model):
#     # Class attributes for SQLAlchemy
#     __tablename__ = 'user'
#
#     # Table columns
#     id = db.Column(db.Integer, primary_key=True)
#     s_number = db.Column(db.String)
#     first_name = db.Column(db.String)
#     last_name_prefix = db.Column(db.String)
#     last_name = db.Column(db.String)
#     date_of_birth = db.Column(db.DateTime)
#     has_sdd_mandate = db.Column(db.Boolean)
#     profile_picture = db.Column(db.String)
#     created = db.Column(db.DateTime)
#     last_updated = db.Column(db.DateTime)
#
#     # def __init__(self, s_number: str, id: int, date_of_birth: datetime, first_name: str, last_name: str,
#     #              last_name_prefix: str = '', has_sdd_mandate: bool = False, profile_picture: dict = ''):
#     def __init__(self, id: int, s_number: str, first_name: str, last_name: str,
#                  date_of_birth: date, last_name_prefix: str = None, has_sdd_mandate: bool = False,
#                  profile_picture: str = None):
#         """
#         Create a new User object.
#
#         :param s_number: Student or Employee number (Congressus user name)
#         :param id: Congressus user id
#         :param date_of_birth: Date of Birth (ISO formatted datetime string)
#         :param first_name: First Name
#         :param last_name: Last Name
#         :param last_name_prefix: Last Name Prefix
#         :param has_sdd_mandate: Has this user signed their SDD mandate
#         :param profile_picture: Dict with URL strings to profile pictures
#         """
#         self.s_number = s_number
#         self.id = id
#         self.first_name = first_name
#         self.last_name_prefix = last_name_prefix
#         self.last_name = last_name
#         self.date_of_birth = date_of_birth
#         self.has_sdd_mandate = has_sdd_mandate
#         self.profile_picture = profile_picture
#         self.created = datetime.now()
#         self.last_updated = datetime.now()
#
#     def update(self, **kwargs):
#         """
#         Update this user's data fields.
#
#         :param kwargs: The fields are updated with keyword arguments.
#         """
#         self.last_updated = datetime.now()
#
#         # If no kwarg is given for an attribute, set it to the already stored attribute
#         self.s_number = kwargs.get('s_number', self.s_number)
#         self.id = kwargs.get('id', self.id)
#         self.first_name = kwargs.get('first_name', self.first_name)
#         self.last_name_prefix = kwargs.get('last_name_prefix', self.last_name_prefix)
#         self.last_name = kwargs.get('last_name', self.last_name)
#         self.date_of_birth = kwargs.get('date_of_birth', self.date_of_birth)
#         self.has_sdd_mandate = kwargs.get('has_sdd_mandate', self.has_sdd_mandate)
#         self.profile_picture = kwargs.get('profile_picture', self.profile_picture)

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/database.sqlite'

db = SQLAlchemy()

admin_manager = LoginManager()

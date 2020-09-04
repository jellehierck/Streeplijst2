from flask_sqlalchemy import SQLAlchemy

SQLALCHEMY_DATABASE_URL = 'sqlite:///instance/database.sqlite'

db = SQLAlchemy()

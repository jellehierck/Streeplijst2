from flask_sqlalchemy import SQLAlchemy

SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/database.sqlite'

db = SQLAlchemy()

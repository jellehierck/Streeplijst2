from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL = 'sqlite:///instance/database.sqlite'
engine = create_engine(SQLALCHEMY_DATABASE_URL, convert_unicode=True)

db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    # noinspection PyUnresolvedReferences
    import streeplijst2.streeplijst
    Base.metadata.create_all(bind=engine)

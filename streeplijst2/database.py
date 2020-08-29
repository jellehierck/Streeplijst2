from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///C:\\Users\\Jelle\\PycharmProjects\\Streeplijst2\\instance\\database.db',
                       convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    import streeplijst2.streeplijst
    Base.metadata.create_all(bind=engine)
